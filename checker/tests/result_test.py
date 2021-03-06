# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.

from checker.base import BakeryTestCase as TestCase, tags
import fontforge
import unicodedata
import yaml
import os
import magic

from fontTools import ttLib

class FontToolsTest(TestCase):
    targets = ['result']
    tool = 'FontTools'
    name = __name__
    path = '.'

    def setUp(self):
        self.font = ttLib.TTFont(self.path)

    def test_tables(self):
        """ List of tables that shoud be in font file """
        # xen: actually I take this list from most popular open font Open Sans,
        # belive that it is most mature.
        # This list should be reviewed
        tables = ['GlyphOrder', 'head', 'hhea', 'maxp', 'OS/2', 'hmtx',
            'cmap', 'fpgm', 'prep', 'cvt ', 'loca', 'glyf', 'name',  # 'kern',
            'post', 'gasp', 'GDEF', 'GPOS', 'GSUB', 'DSIG']

        for x in self.font.keys():
            self.assertIn(x, tables, msg="%s table not found in table list" % x)

    def test_tables_no_kern(self):
        """ Check that no KERN table exists """
        self.assertNotIn('kern', self.font.keys())

    def test_table_gasp_type(self):
        """ Font table gasp should be 15 """
        keys = self.font.keys()
        self.assertIn('gasp', keys, msg="GASP table not found")
        self.assertEqual(type({}), type(self.font['gasp'].gaspRange),
            msg="GASP table: gaspRange method value have wrong type")
        self.assertTrue(65535 in self.font['gasp'].gaspRange)
        # XXX: Needs review
        self.assertEqual(self.font['gasp'].gaspRange[65535], 15)

    def test_metrics_linegaps_are_zero(self):
        """ All values for linegap in 'hhea' and 'OS/2' tables
        should be equal zero """
        self.assertEqual(self.font['hhea'].lineGap, 0)
        self.assertEqual(self.font['OS/2'].sTypoLineGap, 0)

    def test_metrics_ascents_equal_max_bbox(self):
        """ Value for ascents in 'hhea' and 'OS/2' tables should be equal
        to value of glygh with biggest yMax"""

        ymax = 0
        for g in self.font['glyf'].glyphs:
            char = self.font['glyf'][g]
            if hasattr(char, 'yMax') and ymax < char.yMax:
                ymax = char.yMax

        self.assertEqual(self.font['hhea'].ascent, ymax)
        self.assertEqual(self.font['OS/2'].sTypoAscender, ymax)
        self.assertEqual(self.font['OS/2'].usWinAscent, ymax)

    def test_metrics_descents_equal_min_bbox(self):
        """ Value for descents in 'hhea' and 'OS/2' tables should be equal
        to value of glygh with smallest yMin"""

        ymin = 0
        for g in self.font['glyf'].glyphs:
            char = self.font['glyf'][g]
            if hasattr(char, 'yMin') and ymin > char.yMin:
                ymin = char.yMin

        self.assertEqual(self.font['hhea'].descent, ymin)
        self.assertEqual(self.font['OS/2'].sTypoDescender, ymin)
        self.assertEqual(self.font['OS/2'].usWinDescent, ymin)


from fontaine.font import Font
import re


class FontaineTest(TestCase):
    targets = ['result']
    tool = 'pyfontaine'
    name = __name__
    path = '.'

    def setUp(self):
        self.font = Font(self.path)
        # You can use ipdb here to interactively develop tests!
        # Uncommand the next line, then at the iPython prompt: print(self.path)
        # import ipdb; ipdb.set_trace()

    # def test_ok(self):
    #     """ This test succeeds """
    #     self.assertTrue(True)
    #
    # def test_failure(self):
    #     """ This test fails """
    #     self.assertTrue(False)
    #
    # def test_error(self):
    #     """ Unexpected error """
    #     1 / 0
    #     self.assertTrue(False)

    def test_charMaker(self):
        # import ipdb; ipdb.set_trace()
        pattern = re.compile('[\W_]+')
        functionTemplate = """def test_charset_%s(self, p): self.test_charset_%s.__func__.__doc__ = "Is %s covered 100%%?"; self.assertTrue(p == 100)"""
        for orthographyTuple in self.font.get_orthographies():
            charmap = orthographyTuple[0]
            percent = orthographyTuple[2]
            shortname = pattern.sub('', charmap.common_name)
            print "TODO: This doesn't work yet..."
            print functionTemplate % (shortname, shortname, charmap.common_name)
            print 'test_charset_%s(self, 100)' % shortname
            exec functionTemplate % (shortname, shortname, charmap.common_name)
            exec 'test_charset_%s(self, 100)' % shortname


class FontForgeSimpleTest(TestCase):
    targets = ['result']
    tool = 'FontForge'
    name = __name__
    path = '.'

    def setUp(self):
        self.font = fontforge.open(self.path)
        # You can use ipdb here to interactively develop tests!
        # Uncommand the next line, then at the iPython prompt: print(self.path)
        # import ipdb; ipdb.set_trace()

    # def test_ok(self):
    #     """ This test succeeds """
    #     self.assertTrue(True)
    #
    # def test_failure(self):
    #     """ This test fails """
    #     self.assertTrue(False)
    #
    # def test_error(self):
    #     """ Unexpected error """
    #     1 / 0
    #     self.assertTrue(False)

    def test_is_fsType_not_set(self):
        """Is the OS/2 table fsType set to 0?"""
        self.assertEqual(self.font.os2_fstype, 1)

    def test_nbsp(self):
        """Check if 'NO-BREAK SPACE' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('NO-BREAK SPACE')) in self.font)

    def test_space(self):
        """Check if 'SPACE' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('SPACE')) in self.font)

    @tags('required',)
    def test_nbsp_and_space_glyphs_width(self):
        """ Nbsp and space glyphs should have the same width"""
        space = 0
        nbsp = 0
        for x in self.font.glyphs():
            if x.unicode == 160:
                nbsp = x.width
            elif x.unicode == 32:
                space = x.width
        self.assertEqual(space, nbsp)

    def test_euro(self):
        """Check if 'EURO SIGN' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('EURO SIGN')) in self.font)


class MetadataJSONTest(TestCase):
    targets = ['result']
    tool = 'FontForge'
    name = __name__
    path = '.'
    longMessage = True

    def setUp(self):
        self.font = fontforge.open(self.path)
        #
        medatata_path = os.path.join(os.path.dirname(self.path), 'METADATA.json')
        self.metadata = yaml.load(open(medatata_path, 'r').read())
        self.fname = os.path.splitext(self.path)[0]

    @tags('required',)
    def test_metadata_family(self):
        """ Font and METADATA.json have the same name """
        self.assertEqual(self.font.familyname, self.metadata.get('name', None))

    def test_metadata_font_have_regular(self):
        """ According GWF standarts font should have Regular style. """
        # this tests will appear in each font
        have = False
        for i in self.metadata['fonts']:
            if i['fullName'].endswith('Regular'):
                have = True

        self.assertTrue(have)

    @tags('required',)
    def test_metadata_regular_is_400(self):
        """ Usually Regular should be 400 """
        have = False
        for i in self.metadata['fonts']:
            if i['fullName'].endswith('Regular') and int(i.get('weight', 0)) == 400:
                have = True

        self.assertTrue(have)

    def test_metadata_regular_is_normal(self):
        """ Usually Regular should be normal style """
        have = False
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', '').endswith('Regular') and x.get('style', '') == 'normal':
                have = True

        self.assertTrue(have)

    def test_metadata_wight_in_range(self):
        """ Font weight should be in range from 100 to 900, step 100 """

        rcheck = lambda x: True if x in range(100, 1000, 100) else False
        self.assertTrue(all([rcheck(x) for x in self.metadata.get('fonts', None)]))

    styles = ['Thin', 'ThinItalic', 'ExtraLight',
        'ExtraLightItalic', 'Light', 'LightItalic', 'Regular', 'Italic',
        'Medium', 'MediumItalic', 'SemiBold', 'SemiBoldItalic', 'Bold',
        'BoldItalic', 'ExtraBold', 'ExtraBoldItalic', 'Black', 'BlackItalic']

    italic_styles = ['ThinItalic', 'ExtraLightItalic', 'LightItalic', 'Italic',
        'MediumItalic', 'SemiBoldItalic', 'BoldItalic', 'ExtraBoldItalic',  'BlackItalic']

    # test each key for font item:
    # {
    #   "name": "Merritest", --- doesn't incule style name
    #   "postScriptName": "Merritest-Bold", ---
    #   "fullName": "Merritest Bold", ---
    #   "style": "normal",
    #   "weight": 700,
    #   "filename": "Merritest-Bold.ttf", ---
    #   "copyright": "Merriweather is a medium contrast semi condesed typeface
    #         designed to be readable at very small sizes. Merriweather is
    #         traditional in feeling despite a the modern shapes it has adopted
    #         for screens."
    # },

    def test_metadata_fonts_exists(self):
        """ METADATA.json font propery should exists """
        self.assertTrue(self.metadata.get('fonts', False))

    def test_metadata_fonts_list(self):
        """ METADATA.json font propery should be list """
        self.assertEqual(type(self.metadata.get('fonts', False)), type([]))

    def test_metadata_fonts_fields(self):
        """ METADATA.json "fonts" property items should have "name", "postScriptName",
        "fullName", "style", "weight", "filename", "copyright" keys """
        keys = ["name", "postScriptName", "fullName", "style", "weight",
                "filename", "copyright"]
        for x in self.metadata.get("fonts", None):
            for j in keys:
                self.assertTrue(j in x)

    def test_metadata_font_name_canonical(self):
        """ METADATA.json fonts 'name' property should be same as font familyname """
        self.assertTrue(all([x['name'] == self.font.familyname for x in self.metadata.get('fonts', None)]))

    def test_metadata_postscript_canonical(self):
        """ METADATA.json fonts postScriptName should be [font familyname]-[style].
        Alowed styles are: 'Thin', 'ThinItalic', 'ExtraLight', 'ExtraLightItalic',
        'Light', 'LightItalic', 'Regular', 'Italic', 'Medium', 'MediumItalic',
        'SemiBold', 'SemiBoldItalic', 'Bold', 'BoldItalic', 'ExtraBold',
        'ExtraBoldItalic', 'Black', 'BlackItalic' """
        self.assertTrue(all(
             [any([x['postScriptName'].endswith("-" + i) for i in self.styles]) for x in self.metadata.get('fonts', None)]
             ))

    def test_metadata_font_fullname_canonical(self):
        """ METADATA.json fonts fullName property should be '[font.familyname] [font.style]' format (w/o quotes)"""
        for x in self.metadata.get("fonts", None):
            style = None
            fn = x.get('fullName', None)
            for i in self.styles:
                if fn.endswith(i):
                    style = i
                    break
            self.assertTrue(style)
            self.assertEqual("%s %s" % (self.font.familyname, style), fn)

    def test_metadata_font_filename_canonical(self):
        """ METADATA.json fonts filename property should be [font.familyname]-[font.style].ttf format."""
        for x in self.metadata.get("fonts", None):
            style = None
            fn = x.get('filename', None)
            for i in self.styles:
                if fn.endswith("-%s.ttf" % i):
                    style = i
                    break
            self.assertTrue(style, msg="%s not in canonical format" % x.get('filename', None))
            self.assertEqual("%s-%s.ttf" % (self.font.familyname, style), fn)

    def test_metadata_fonts_no_dupes(self):
        """ METADATA.json fonts propery only should have uniq values """
        fonts = {}
        for x in self.metadata.get('fonts', None):
            self.assertFalse(x.get('fullName', '') in fonts)
            fonts[x.get('fullName', '')] = x

        self.assertEqual(len(set(fonts.keys())), len(self.metadata.get('fonts', None)))

    def test_metadata_contains_current_font(self):
        """ METADATA.json should contains testing font, under canonic name"""
        font = None
        current_font = "%s %s" % (self.font.familyname, self.font.weight)
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', None) == current_font:
                font = x
                break

        self.assertTrue(font)

    def test_metadata_fonts_fields_have_fontname(self):
        """ METADATA.json fonts items fields "name", "postScriptName",
        "fullName", "filename" contains font name right format """
        for x in self.metadata.get('fonts', None):
            self.assertIn(self.font.familyname, x.get('name', ''))
            self.assertIn(self.font.familyname, x.get('fullName', ''))
            self.assertIn("".join(str(self.font.familyname).split()),
                            x.get('filename', ''))
            self.assertIn("".join(str(self.font.familyname).split()),
                            x.get('postScriptName', ''))

    def test_metadata_font_style_italic_follow_internal_data(self):
        """ METADATA.json fonts style property should be italic if font is italic."""
        font = None
        current_font = "%s %s" % (self.font.familyname, self.font.weight)
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', None) == current_font:
                font = x
                break
        self.assertTrue(font)
        if int(self.font.italicangle) == 0:
            self.assertEqual(font.get('style', None), 'normal')
        else:
            self.assertEqual(font.get('style', None), 'italic')

    def test_font_weight_is_canonical(self):
        """ Font wight property is from canonical styles list"""
        self.assertIn(self.font.weight, self.styles)

    def test_font_name_canonical(self):
        """ Font name is canonical """
        self.assertTrue(any([self.font.fontname.endswith(x) for x in self.styles]))

    def test_font_file_name_canonical(self):
        """ Font name is canonical """
        name = os.path.basename(self.path)
        canonic_name = "%s-%s.ttf" % (self.font.familyname, self.font.weight)
        self.assertEqual(name, canonic_name)

    def test_menu_file_exists(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(os.path.exists("%s.menu" % self.fname))

    def test_menu_file_is_canonical(self):
        """ Menu file should be [font.familyname]-[font.weight].menu """
        name = "%s.menu" % self.fname
        canonic_name = "%s-%s.menu" % (self.font.familyname, self.font.weight)
        self.assertEqual(name, canonic_name)

    def test_menu_file_is_font(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(magic.from_file("%s.menu" % self.fname), 'TrueType font data')

    def test_metadata_have_subset(self):
        """ METADATA.json shoyld have 'subsets' property """
        self.assertTrue(self.metadata.get('subsets', None))

    subset_list = ['menu', 'latin', 'latin_ext', 'vietnamese', 'greek',
                    'cyrillic', 'cyrillic_ext', 'arabic']

    def test_metadata_subsets_names_are_correct(self):
        """ METADATA.json 'subset' property can have only allowed values from list:
        ['menu', 'latin','latin_ext', 'vietnamese', 'greek', 'cyrillic',
        'cyrillic_ext', 'arabic'] """
        self.assertTrue(all([x in self.subset_list for x in self.metadata.get('subsets', None)]))

    def test_subsets_exists_font(self):
        """ Each font file should have its own set of subsets
        defined in METADATA.json """
        for x in self.metadata.get('fonts', None):
            for i in self.metadata.get('subsets', None):
                name = "%s.%s" % (self.fname, i)
                self.assertTrue(os.path.exists(name), msg="'%s' not found" % name)

    def test_subsets_exists_opentype(self):
        """ Each font file should have its own set of opentype file format
        subsets defined in METADATA.json """
        for x in self.metadata.get('fonts', None):
            for i in self.metadata.get('subsets', None):
                name = "%s.%s-opentype" % (self.fname, i)
                self.assertTrue(os.path.exists(name), msg="'%s' not found" % name)

    def test_subsets_files_mime_correct(self):
        """ Each subset file should be correct binary files """
        for x in self.metadata.get('fonts', None):
            for i in self.metadata.get('subsets', None):
                name = "%s.%s" % (self.fname, i)
                self.assertEqual(magic.from_file(name, mime=True), 'application/x-font-ttf')

    def test_subsets_opentype_files_mime_correct(self):
        """ Each subset file should be correct binary files """
        for x in self.metadata.get('fonts', None):
            for i in self.metadata.get('subsets', None):
                name = "%s.%s-opentype" % (self.fname, i)
                self.assertEqual(magic.from_file(name, mime=True), 'application/x-font-ttf')

    def test_menu_have_chars(self):
        """ Test does .menu file have chars needed for METADATA family key """
        from checker.tools import combine_subsets
        for x in self.metadata.get('subsets', None):
            name = "%s.%s" % (self.fname, x)

            menu = fontforge.open(name)
            subset_chars = combine_subsets([x, ])
            self.assertTrue(all([i in menu for i in subset_chars]))

    def test_subset_file_smaller_font_file(self):
        """ Subset files should be smaller than font file """
        for x in self.metadata.get('subsets', None):
            name = "%s.%s" % (self.fname, x)
            self.assertLess(os.path.getsize(name), os.path.getsize(self.path))

    weights = {
        'Thin': 100,
        'ThinItalic': 100,
        'ExtraLight': 200,
        'ExtraLightItalic': 200,
        'Light': 300,
        'LightItalic': 300,
        'Regular': 400,
        'Italic': 400,
        'Medium': 500,
        'MediumItalic': 500,
        'SemiBold': 600,
        'SemiBoldItalic': 600,
        'Bold': 700,
        'BoldItalic': 700,
        'ExtraBold': 800,
        'ExtraBoldItalic': 800,
        'Black': 900,
        'BlackItalic': 900,
    }

    def test_metadata_value_match_font_weight(self):
        """Check that METADATA font.weight keys match font internal metadata"""
        fonts = {}
        for x in self.metadata.get('fonts', None):
            fonts[x.get('fullName', '')] = x

        self.assertEqual(self.weights.get(self.font.weight, 0),
                            fonts.get(self.font.fullname, {'weight': ''}).get('weight', 0))

    def test_metadata_font_style_same_all_fields(self):
        """ METADATA.json fonts properties "name" "postScriptName" "fullName"
        "filename" should have the same style """
        weights_table = {
            'Thin': 'Thin',
            'ThinItalic': 'Thin Italic',
            'ExtraLight': 'Extra Light',
            'ExtraLightItalic': 'Extra Light Italic',
            'Light': 'Light',
            'LightItalic': 'Light Italic',
            'Regular': 'Regular',
            'Italic': 'Italic',
            'Medium': 'Medium',
            'MediumItalic': 'Medium Italic',
            'SemiBold': 'Semi Bold',
            'SemiBoldItalic': 'Semi Bold Italic',
            'Bold': 'Bold',
            'BoldItalic': 'Bold Italic',
            'ExtraBold': 'Extra Bold',
            'ExtraBoldItalic': 'Extra Bold Italic',
            'Black': 'Black',
            'BlackItalic': 'Black Italic',

        }

        for x in self.metadata.get('fonts', None):
            if x.get('postScriptName', '') != self.font.familyname:
                # this is not regular style
                _style = x["postScriptName"].split('-').pop(-1)
                self.assertIn(_style, weights_table.keys(),
                                msg="Style name not from expected list")
                self.assertEqual("%s %s" % (self.font.familyname,
                        weights_table.keys[_style]), x.get("fullName", ''))
            else:
                _style = 'Regular'

            self.assertEqual("%s-%s.ttf" % (self.font.familyname,
                                                _style), x.get("filename", ''))

    def test_metadata_font_style_italic_correct(self):
        """ METADATA.json fonts properties "name" "postScriptName" "fullName"
        "filename" should have the same style """
        italics_styles = {
            'ThinItalic': 'Thin Italic',
            'ExtraLight': 'Extra Light',
            'ExtraLightItalic': 'Extra Light Italic',
            'LightItalic': 'Light Italic',
            'Italic': 'Italic',
            'MediumItalic': 'Medium Italic',
            'SemiBoldItalic': 'Semi Bold Italic',
            'BoldItalic': 'Bold Italic',
            'ExtraBoldItalic': 'Extra Bold Italic',
            'BlackItalic': 'Black Italic',
        }

        for x in self.metadata.get('fonts', None):
            if x.get('postScriptName', '') != self.font.familyname:
                # this is not regular style
                _style = x["postScriptName"].split('-').pop(-1)
                if _style in italics_styles.keys():
                    self.assertEqual(x.get('style', ''), 'italic')
                else:
                    self.assertEqual(x.get('style', ''), 'normal')

    @tags('required')
    def test_em_is_1000(self):
        """ Font em should be equal 1000 """
        self.assertEqual(self.font.em, 1000,
                            msg="Font em value is %s, required 1000" % self.font.em)

    def test_font_italicangle_is_zero_or_negative(self):
        """ font.italicangle property can be zero or negative """
        if self.font.italicangle == 0:
            self.assertEqual(self.font.italicangle, 0)
        else:
            self.assertLess(self.font.italicangle, 0)

    def test_font_italicangle_limits(self):
        """ font.italicangle maximum abs(value) can be between 0 an 45 degree """
        self.assertTrue(abs(self.font.italicangle) >= 0 and abs(self.font.italicangle) <= 45)

    def test_font_is_font(self):
        """ File provided as parameter is TTF font file """
        self.assertTrue(magic.from_file(self.path, mime=True),
                        'application/x-font-ttf')

    def test_metadata_keys(self):
        """ METADATA.json should have top keys: ["name", "designer", "license", "visibility", "category",
        "size", "dateAdded", "fonts", "subsets"] """

        top_keys = ["name", "designer", "license", "visibility", "category",
                    "size", "dateAdded", "fonts", "subsets"]

        for x in top_keys:
            self.assertIn(x, self.metadata, msg="Missing %s key" % x)

    def test_metadata_fonts_key_list(self):
        """ METADATA.json font key should be list """
        self.assertEqual(type(self.metadata.get('fonts', '')), type([]))

    def test_metadata_subsets_key_list(self):
        """ METADATA.json subsets key should be list """
        self.assertEqual(type(self.metadata.get('subsets', '')), type([]))

    def test_metadata_fonts_items_dicts(self):
        """ METADATA.json fonts key items are dicts """
        for x in self.metadata.get('fonts', None):
            self.assertEqual(type(x), type({}), msg="type(%s) is not dict" % x)

    def test_metadata_subsets_items_string(self):
        """ METADATA.json subsets key items are strings """
        for x in self.metadata.get('subsets', None):
            self.assertEqual(type(x), type(""), msg="type(%s) is not dict" % x)

    def test_metadata_top_keys_types(self):
        """ METADATA.json should have proper top keys types """
        self.assertEqual(type(self.metadata.get("name", None)),
                            type(""), msg="name key type invalid")
        self.assertEqual(type(self.metadata.get("designer", None)),
                            type(""), msg="designer key type invalid")
        self.assertEqual(type(self.metadata.get("license", None)),
                            type(""), msg="license key type invalid")
        self.assertEqual(type(self.metadata.get("visibility", None)),
                            type(""), msg="visibility key type invalid")
        self.assertEqual(type(self.metadata.get("category", None)),
                            type(""), msg="category key type invalid")
        self.assertEqual(type(self.metadata.get("size", None)),
                            type(0), msg="size key type invalid")
        self.assertEqual(type(self.metadata.get("dateAdded", None)),
                            type(""), msg="dateAdded key type invalid")

    def test_metadata_font_keys_types(self):
        """ METADATA.json fonts items dicts items should have proper types """
        for x in self.metadata.get("fonts", None):
            self.assertEqual(type(self.metadata.get("name", None)),
                                type(""), msg="name key type invalid for %s " % x)
            self.assertEqual(type(self.metadata.get("postScriptName", None)),
                                type(""), msg="postScriptName key type invalid for %s " % x)
            self.assertEqual(type(self.metadata.get("fullName", None)),
                                type(""), msg="fullName key type invalid for %s " % x)
            self.assertEqual(type(self.metadata.get("style", None)),
                                type(""), msg="style key type invalid for %s " % x)
            self.assertEqual(type(self.metadata.get("weight", None)),
                                type(0), msg="weight key type invalid for %s " % x)
            self.assertEqual(type(self.metadata.get("filename", None)),
                                type(""), msg="filename key type invalid for %s " % x)
            self.assertEqual(type(self.metadata.get("copyright", None)),
                                type(""), msg="copyright key type invalid for %s " % x)

    def test_metadata_no_unknown_top_keys(self):
        """ METADATA.json don't have unknown top keys """
        top_keys = ["name", "designer", "license", "visibility", "category",
                    "size", "dateAdded", "fonts", "subsets"]

        for x in self.metadata.keys():
            self.assertIn(x, top_keys, msg="%s found unknown top key" % x)

    def test_metadata_fonts_no_unknown_keys(self):
        """ METADATA.json fonts don't have unknown top keys """
        fonts_keys = ["name", "postScriptName", "fullName", "style", "weight",
                        "filename", "copyright"]
        for x in self.metadata.get("fonts", None):
            for i in x.keys():
                self.assertIn(i, fonts_keys,
                                msg="%s found unknown top key in %s" % (i, x))

    def test_metadata_subsets_values(self):
        """ METADATA.json subsets should have at least 'menu' and 'latin' """
        self.assertIn('menu', self.metadata.get('subsets', []),
                        msg="Subsets missing menu")
        self.assertIn('latin', self.metadata.get('subsets', []),
                        msg="Subsets missing latin")

    def test_metadata_copyright(self):
        """ METDATA.json fonts copyright string is the same for all items """

        copyright = None

        for x in self.metadata.get('fonts', None):
            copyright = x.get('copyright', None)
            break

        if copyright:
            for x in self.metadata.get('fonts', None):
                self.assertEqual(x.get('copyright', ''), copyright,
                    msg="%s have different copyright string" % x.get('name', ''))

    def test_metadata_license(self):
        """ METADATA.json license is 'Apache2' or 'OFL' """
        licenses = ['Apache2', 'OFL']
        self.assertIn(self.metadata.get('license', ''), licenses)

    def test_metadata_copyright_reserved(self):
        """ Copyright string should contains 'Reserved Font Name' substring """
        for x in self.metadata.get('fonts', None):
            self.assertIn('Reserved Font Name', x.get('copyright', ''))

    def test_metadata_copyright_size(self):
        """ Copyright string should be less than 500 chars """
        for x in self.metadata.get('fonts', None):
            self.assertLessEqual(len(x.get('copyright', '')), 500)

    def test_copyrighttxt_exists(self):
        """ Font folder should contains COPYRIGHT.txt """
        self.assertTrue(os.path.exists(os.path.join(
            os.path.dirname(self.path), 'COPYRIGHT.txt')))

    def test_description_exists(self):
        """ Font folder should contains DESCRIPTION.en_us.html """
        self.assertTrue(os.path.exists(os.path.join(
            os.path.dirname(self.path), 'DESCRIPTION.en_us.html')))

    def test_licensetxt_exists(self):
        """ Font folder should contains LICENSE.txt """
        self.assertTrue(os.path.exists(os.path.join(
            os.path.dirname(self.path), 'LICENSE.txt')))

    def test_fontlogtxt_exists(self):
        """ Font folder should contains FONTLOG.txt """
        self.assertTrue(os.path.exists(os.path.join(
            os.path.dirname(self.path), 'FONTLOG.txt')))


    # def test_copyright_file_filled(self):
    #     """ COPYRIGHT.txt file """
