from __future__ import print_function
import argparse
import json
import os
import sys

class InstagramFilter:
    ''''''
    def __init__(self, options):
        ''''''
        self.options = options

        self.input_json = []
        self.keyword_set = []
        self.output_json = []
        self.selfie_set = set(['selfie', 'selfieee', 'selfiedrunk'])

        # Load keyword file, in same directory as this file
        source_dir = os.path.abspath(os.path.dirname(__file__))
        keyword_file = os.path.join(source_dir, 'alcohol_keywords.txt')
        with open (keyword_file) as f:
            keyword_list = f.read().splitlines()
            self.keyword_set = set(keyword_list)
            print('Imported keyword count: {}'.format(len(self.keyword_set)))
        if not keyword_list:
            raise Exception('No keyword_list')


    def load_input(self):
        '''Loads and parses input file
        '''
        if not options.input_filename:
            raise Exception('No input_filename specified in options')

        with open(self.options.input_filename) as f:
            text = f.read()
            self.input_json = json.loads(text)

        if not text:
            raise Exception('Input file missing, empty, or unreadable ({})' \
                .format(self.options.input_filename))
        print('Number of input posts: {}'.format(len(self.input_json)))


    def filter_post(self, post):
        ''''''
        # Get caption and tags
        caption_text = post.get('caption', {}).get('text')
        tag_list = post.get('tags')
        tag_set = set(tag_list)

        # Optionally EXCLUDE tags missing selfie words
        if self.options.filter_selfie_tags:
            match_set = self.selfie_set.intersection(tag_set)
            if not match_set:
                return False

        # Optionally INCLUDE tags matching keywords
        if self.options.include_alcohol_tags:
            match_set = self.keyword_set.intersection(tag_set)
            if match_set:
                return True

        # Last - INCLUDE captions matching keywords
        if not caption_text:
            return False

        word_list = caption_text.lower().split()
        word_set = set(word_list)
        match_set = self.keyword_set.intersection(word_set)
        if not match_set:
            return False

        # (else)
        return True

    def filter_posts(self):
        ''''''
        match_count = 0
        for post in self.input_json:
            match = self.filter_post(post)
            if match:
                match_count += 1
                if self.options.verbose_level > 0:
                    print('match {}'.format(post.get('id')))
            if match and self.options.output_filename:
                self.output_json.append(post)
        print('Number of matching posts: {}'.format(match_count))


    def write_output(self):
        ''''''
        with open(self.options.output_filename, 'w') as f:
            output_text = json.dumps(self.output_json)
            f.write(output_text)
            f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filename', required=True, \
        help='Input file (json)')
    parser.add_argument('-o', '--output_filename', help='Output filename (json)')
    parser.add_argument('-a', '--include_alcohol_tags', action='store_true', \
        help='include posts with tags matching alcohol words')
    parser.add_argument('-s', '--filter_selfie_tags', action='store_true', \
        help='exclude posts with no tags matching selfie words')
    parser.add_argument('-v', '--verbose_level', default=0, \
        help='Verbose output level (default 0)')
    options = parser.parse_args()

    print(options)
    filter = InstagramFilter(options)

    print('Loading input file {}'.format(options.input_filename))
    filter.load_input()

    print('Running filter')
    filter.filter_posts()

    if options.output_filename:
        print('Writing output file {}'.format(options.output_filename))
        filter.write_output()
