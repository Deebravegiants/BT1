# [M] Phpsysinfo Cross Site Request Forgery (CSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-67gv-xrw7-p72w
CVE: CVE-2023-49006
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-19
Source: https://github.com/advisories/GHSA-67gv-xrw7-p72w
Type: github-advisory

## Affected
- Packagist: `phpsysinfo/phpsysinfo` — affected >=0 <3.4.3

## Details
Cross Site Request Forgery (CSRF) vulnerability in Phpsysinfo version 3.4.3 allows a remote attacker to obtain sensitive information via a crafted page in the XML.php file.  Phpsysinfo 3.4.3 disables the functionality by default but the users may enable the vulnerable functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49006
- https://github.com/Hebing123/cve/issues/5
- https://github.com/phpsysinfo/phpsysinfo/commit/4f2cee505e4f2e9b369a321063ff2c5e0c34ba45
- https://github.com/phpsysinfo/phpsysinfo
- https://huntr.com/bounties/ca6d669f-fd82-4188-aae2-69e08740d982
