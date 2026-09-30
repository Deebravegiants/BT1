# [C] CVE-2017-9364

## Summary
Severity: Critical
Advisory: CVE-2017-9364
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9364
Type: osv

## Details
Unrestricted File Upload exists in BigTree CMS through 4.2.18: if an attacker uploads an 'xxx.pht' or 'xxx.phtml' file, they could bypass a safety check and execute any code.

## References
- https://github.com/bigtreecms/BigTree-CMS/commit/b72293946951cc650eaf51f5d2f62ceac6335e12
- https://github.com/bigtreecms/BigTree-CMS/issues/280
