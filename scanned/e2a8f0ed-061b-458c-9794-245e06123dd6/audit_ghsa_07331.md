# [M] Mistune: Arbitrary File Read via Include directive path traversal

## Summary
Severity: Medium
Advisory: GHSA-r4rv-85jg-w4mf
CVE: CVE-2026-59924
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-r4rv-85jg-w4mf
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
### Summary

A path traversal issue exists in mistune's `Include` directive when markdown files are processed using `md.read()`. A crafted include path can cause files outside the intended markdown directory to be accessed.

### Details

The issue occurs in the `Include.parse()` method where user-supplied paths are joined and normalized without verifying that the resulting path remains within an expected directory.

```python
relpath = self.parse_title(m)
dest = os.path.join(os.path.dirname(source_file), relpath)
dest = os.path.normpath(dest)
```

Because the final path is not restricted to a trusted base directory, path traversal sequences such as `../` may reference files outside the intended location.

### Proof of Concept

Create a markdown file:

```markdown
.. include:: ../../../example.txt
```

Process it using:

```python
import mistune
from mistune.directives import RSTDirective, Include

md = mistune.create_markdown(
    plugins=[RSTDirective([Include()])]
)

result, state = md.read("test.md")
print(result)
```

### Impact

Applications that process untrusted markdown files with the `Include` directive enabled may allow unintended file access. The impact depends on how the feature is used and what files are accessible to the running process.

### Recommended Fix

Validate the resolved path and ensure it remains within an allowed directory before opening the file.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-r4rv-85jg-w4mf
- https://nvd.nist.gov/vuln/detail/CVE-2026-59924
- https://github.com/lepture/mistune/commit/1bef343ade163fc3bb95572b15be720084cdb993
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-2212.yaml
