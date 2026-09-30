# [C] Critical severity vulnerability that affects Haraka

## Summary
Severity: Critical
Advisory: GHSA-w5m8-5v9m-xhx5
CVE: CVE-2016-1000282
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-12
Source: https://github.com/advisories/GHSA-w5m8-5v9m-xhx5
Type: github-advisory

## Affected
- npm: `Haraka` — affected >=0 <2.8.9

## Details
Haraka version 2.8.8 and earlier comes with a plugin for processing attachments for zip files. Versions 2.8.8 and earlier can be vulnerable to command injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000282
- https://github.com/advisories/GHSA-w5m8-5v9m-xhx5
- https://github.com/outflanknl/Exploits/blob/master/harakiri-CVE-2016-1000282.py
