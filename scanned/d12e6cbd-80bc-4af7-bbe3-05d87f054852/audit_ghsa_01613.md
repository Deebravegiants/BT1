# [M] malicious SVG attachment causing stored XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4q96-6xhq-ff43
CVE: CVE-2020-15275
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-11-11
Source: https://github.com/advisories/GHSA-4q96-6xhq-ff43
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=0 <1.9.11

## Details
### Impact
An attacker with `write` permissions can upload an SVG file that contains malicious javascript. This javascript will be executed in a user's browser when the user is viewing that SVG file on the wiki.

### Patches
Users are strongly advised to upgrade to a patched version.

MoinMoin Wiki 1.9.11 has the necessary fixes and also contains other important fixes.

### Workarounds
It is not advised to work around this, but to upgrade MoinMoin to a patched version.

That said, a work around via a Content Security Policy in the web server might be possible.

Also, it is of course helpful if you give `write` permissions (which include uploading attachments) only to trusted users.

### For more information
If you have any questions or comments about this advisory, email me at [twaldmann@thinkmo.de](mailto:twaldmann@thinkmo.de).

### Credits

This vulnerability was discovered by:

Catarina Leite from the Checkmarx SCA AppSec team

## References
- https://github.com/moinwiki/moin-1.9/security/advisories/GHSA-4q96-6xhq-ff43
- https://nvd.nist.gov/vuln/detail/CVE-2020-15275
- https://github.com/moinwiki/moin-1.9/commit/31de9139d0aabc171e94032168399b4a0b2a88a2
- https://advisory.checkmarx.net/advisory/CX-2020-4285
- https://github.com/moinwiki/moin-1.9
- https://github.com/moinwiki/moin-1.9/releases/tag/1.9.11
- https://github.com/pypa/advisory-database/tree/main/vulns/moin/PYSEC-2020-241.yaml
- https://pypi.org/project/moin
