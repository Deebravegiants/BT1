# [M] Potential double free of buffer during string decoding

## Summary
Severity: Medium
Advisory: GHSA-fm67-cv37-96ff
CVE: CVE-2022-31117
CWE: CWE-415
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-05
Source: https://github.com/advisories/GHSA-fm67-cv37-96ff
Type: github-advisory

## Affected
- PyPI: `ujson` — affected >=0 <5.4.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

When an error occurs while reallocating the buffer for string decoding, the buffer gets freed twice.

Due to how UltraJSON uses the internal decoder, this double free is impossible to trigger from Python.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Users should upgrade to UltraJSON 5.4.0.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

There is no workaround.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [UltraJSON](http://github.com/ultrajson/ultrajson/issues)

## References
- https://github.com/ultrajson/ultrajson/security/advisories/GHSA-fm67-cv37-96ff
- https://nvd.nist.gov/vuln/detail/CVE-2022-31117
- https://github.com/ultrajson/ultrajson/commit/9c20de0f77b391093967e25d01fb48671104b15b
- https://github.com/ultrajson/ultrajson
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NAU5N4A7EUK2AMUCOLYDD5ARXAJYZBD2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OPPU5FZP3LCTXYORFH7NHUMYA5X66IA7
