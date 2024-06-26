#! /usr/bin/env python3
"""
Class to generate Markdown documentation pages from parsed module doc strings
"""

from xml.sax.saxutils import escape
import codecs
import os

class MarkdownOutput():
    def __init__(self, module_groups):

        self._outputs = {}

        result = """
# Modules & Commands Reference

The following pages document the PX4 modules, drivers and commands.
They describe the provided functionality, high-level implementation overview and how
to use the command-line interface.

::: info
**This is auto-generated from the source code** and contains the most recent modules documentation.
:::

It is not a complete list and NuttX provides some additional commands
as well (such as `free`). Use `help` on the console to get a list of all
available commands, and in most cases `command help` will print the usage.

Since this is generated from source, errors must be reported/fixed
in the [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) repository.
The documentation pages can be generated by running the following command from
the root of the PX4-Autopilot directory:

```
make module_documentation
```
The generated files will be written to the `modules` directory.

## Categories
"""
        for category in sorted(module_groups):
            result += "- [%s](modules_%s.md)\n" % (category.capitalize(), category)

        self._outputs['main'] = result

        for category in sorted(module_groups):
            result = "# Modules Reference: %s\n" % category.capitalize()
            subcategories = module_groups[category]
            if len(subcategories) > 1:
                result += 'Subcategories:\n'
                for subcategory in subcategories:
                    if subcategory == '':
                        continue
                    subcategory_label = subcategory.replace('_', ' ').title()
                    subcategory_file_name = category+'_'+subcategory
                    result += '- [%s](modules_%s.md)\n' % (subcategory_label, subcategory_file_name)

                    # add a sub-page for the subcategory
                    result_subpage = '# Modules Reference: %s (%s)\n' % \
                        (subcategory_label, category.capitalize())
                    result_subpage += self._ProcessModules(subcategories[subcategory])
                    self._outputs[subcategory_file_name] = result_subpage

            result += '\n' + self._ProcessModules(subcategories[''])
            self._outputs[category] = result

    def _ProcessModules(self, module_list):
        result = ''
        for module in module_list:
            result += "## %s\n" % module.name()
            result += "Source: [%s](https://github.com/PX4/PX4-Autopilot/tree/main/src/%s)\n\n" % (module.scope(), module.scope())
            doc = module.documentation()
            if len(doc) > 0:
                result += "%s\n" % doc
            usage_string = module.usage_string()
            if len(usage_string) > 0:
                result += '<a id="%s_usage"></a>\n### Usage\n```\n%s\n```\n' % (module.name(), usage_string)
        return result

    def Save(self, dirname):
        for output_name in self._outputs:
            output = self._outputs[output_name]
            with codecs.open(os.path.join(dirname, 'modules_'+output_name+'.md'), 'w', 'utf-8') as f:
                f.write(output)
