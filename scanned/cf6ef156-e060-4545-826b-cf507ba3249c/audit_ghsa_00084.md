# [H] Regular Expression Denial of Service in sshpk

## Summary
Severity: High
Advisory: GHSA-2m39-62fm-q8r3
CVE: CVE-2018-3737
CWE: CWE-185, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-08-15
Source: https://github.com/advisories/GHSA-2m39-62fm-q8r3
Type: github-advisory

## Affected
- npm: `sshpk` — affected >=0 <1.13.2

## Details
Versions of `sshpk` before 1.13.2 or 1.14.1 are vulnerable to regular expression denial of service when parsing crafted invalid public keys.


## Recommendation

Update to version 1.13.2, 1.14.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3737
- https://github.com/joyent/node-sshpk/commit/46065d38a5e6d1bccf86d3efb2fb83c14e3f9957
- https://hackerone.com/reports/319593
- https://github.com/advisories/GHSA-2m39-62fm-q8r3
- https://github.com/joyent/node-sshpk/blob/v1.13.1/lib/formats/ssh.js#L17
- https://www.npmjs.com/advisories/606
