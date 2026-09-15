# [C] CVE-2024-37385

## Summary
Severity: Critical
Advisory: CVE-2024-37385
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-07
Source: https://osv.dev/vulnerability/CVE-2024-37385
Type: osv

## Details
Roundcube Webmail before 1.5.7 and 1.6.x before 1.6.7 on Windows allows command injection via im_convert_path and im_identify_path. NOTE: this issue exists because of an incomplete fix for CVE-2020-12641.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.7
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37385.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37385
- https://github.com/roundcube/roundcubemail/commit/5ea9f37ce39374b6124586c0590fec7015d35d7f
