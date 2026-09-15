# [H] python-liquid: Absolute paths escape filesystem loader search path

## Summary
Severity: High
Advisory: GHSA-8p4x-wr7x-3788
CVE: CVE-2026-45017
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-8p4x-wr7x-3788
Type: github-advisory

## Affected
- PyPI: `python-liquid` — affected >=0 <2.2.0

## Details
### Impact
The built-in `FileSystemLoader` and `CachingFileSystemLoader` do not guard against reading files outside their search paths when given an absolute path to resolve. This allows malicious template authors to load and render arbitrary files via the `{% include %}` and `{% render %}` tags. Targeted files would need to contain valid Liquid markup and be readable by the application process.

### Patches
The issue is fixed in version 2.2.0 with the inclusion of a `template_path.is_absolute()` condition in `liquid/builtin/loaders/file_system_loader.py`.

```python
        if os.path.pardir in template_path.parts or template_path.is_absolute():
            raise TemplateNotFoundError(template_name)
```

### Workarounds

Create a custom template loader by inheriting from `FileSystemLoader` and overriding `resolve_path()`. Use an instance of the custom loader as the `loader` argument when instantiating your Liquid environment. 

```python
import os
from pathlib import Path

from liquid import Environment
from liquid import FileSystemLoader
from liquid.exceptions import TemplateNotFoundError


class MyFileSystemLoader(FileSystemLoader):
    def resolve_path(self, template_name: str) -> Path:
        template_path = Path(template_name)

        if self.ext and not template_path.suffix:
            template_path = template_path.with_suffix(self.ext)

        if os.path.pardir in template_path.parts or template_path.is_absolute():
            raise TemplateNotFoundError(template_name)

        for path in self.search_path:
            source_path = path.joinpath(template_path)
            if not source_path.exists():
                continue
            return source_path

        raise TemplateNotFoundError(template_name)


env = Environment(loader=MyFileSystemLoader("path/to/templates/"))
```

## References
- https://github.com/jg-rp/liquid/security/advisories/GHSA-8p4x-wr7x-3788
- https://nvd.nist.gov/vuln/detail/CVE-2026-45017
- https://github.com/jg-rp/liquid
- https://github.com/pypa/advisory-database/tree/main/vulns/python-liquid/PYSEC-2026-192.yaml
