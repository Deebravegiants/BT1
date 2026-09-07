# [H] lxml: Default configuration of iterparse() and ETCompatXMLParser() allows XXE to local files

## Summary
Severity: High
Advisory: GHSA-vfmq-68hx-4jfw
CVE: CVE-2026-41066
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-vfmq-68hx-4jfw
Type: github-advisory

## Affected
- PyPI: `lxml` — affected >=0 <6.1.0

## Details
### Impact
Using either of the two parsers in the default configuration (with `resolve_entities=True`) allows untrusted XML input to read local files.

### Patches
lxml 6.1.0 changes the default to `resolve_entities='internal'`, thus disallowing local file access by default.

### Workarounds
Setting the `resolve_entities` option explicitly to `resolve_entities='internal'` or `resolve_entities=False` disables the local file access.

### Resources
Original report: https://bugs.launchpad.net/lxml/+bug/2146291

The default option was changed to `resolve_entities='internal'` for the normal XML and HTML parsers in lxml 5.0. The default was not changed for `iterparse()` and `ETCompatXMLParser()` at the time. lxml 6.1 makes the safe option the default for all parsers.

## References
- https://github.com/lxml/lxml/security/advisories/GHSA-vfmq-68hx-4jfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-41066
- https://bugs.launchpad.net/lxml/+bug/2146291
- https://github.com/lxml/lxml
- https://github.com/lxml/lxml/releases/tag/lxml-6.1.0
- https://github.com/pypa/advisory-database/tree/main/vulns/lxml/PYSEC-2026-87.yaml
