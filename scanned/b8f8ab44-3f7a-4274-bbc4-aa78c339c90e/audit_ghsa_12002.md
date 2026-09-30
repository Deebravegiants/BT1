# [H] SimpleEval: Objects (including modules) can leak dangerous modules through to direct access inside the sandbox

## Summary
Severity: High
Advisory: GHSA-44vg-5wv2-h2hg
CVE: CVE-2026-32640
CWE: CWE-915, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-44vg-5wv2-h2hg
Type: github-advisory

## Affected
- PyPI: `simpleeval` — affected >=0 <1.0.5

## Details
### Impact
If the objects passed in as `names` to SimpleEval have modules or other disallowed / dangerous objects available as attrs.
Additionally, dangerous functions or modules could be accessed by passing them as callbacks to other safe functions to call.

Examples (found by @ByamB4):

Any module where non-underscore attribute chains reach os or sys:
- os.path, pathlib, shutil, glob (direct .os / .sys attributes)
- statistics (has .sys)
- numpy (has .ctypeslib.os and .f2py.sys)
- urllib.parse (has .warnings.sys)

### Patches
The latest version 1.0.5 has this issue fixed.

### Workarounds
Don't pass in objects or modules which have direct attributes to potentially dangerous items.
Use a wrapper to wrap the potentially vulnerable items (See the ModuleWrapper in version 1.0.5)

## References
- https://github.com/danthedeckie/simpleeval/security/advisories/GHSA-44vg-5wv2-h2hg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32640
- https://github.com/danthedeckie/simpleeval
- https://github.com/danthedeckie/simpleeval/releases/tag/1.0.5
- https://github.com/pypa/advisory-database/tree/main/vulns/simpleeval/PYSEC-2026-132.yaml
- https://lists.debian.org/debian-lts-announce/2026/04/msg00023.html
