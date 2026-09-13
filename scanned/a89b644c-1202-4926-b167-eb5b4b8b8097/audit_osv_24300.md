# [H] Stack Buffer Overflow in editorconfig-core-c

## Summary
Severity: High
Advisory: CVE-2023-0341
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-01-31
Source: https://osv.dev/vulnerability/CVE-2023-0341
Type: osv

## Details
A stack buffer overflow exists in the ec_glob function of editorconfig-core-c before v0.12.6 which allowed an attacker to arbitrarily write to the stack and possibly allows remote code execution. editorconfig-core-c v0.12.6 resolved this vulnerability by bound checking all write operations over the p_pcre buffer.

## References
- https://github.com/editorconfig/editorconfig-core-c/
- https://lists.debian.org/debian-lts-announce/2024/11/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZCFE7DXWAAKDJPRKMXHCACKGKNV37IYZ/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0341.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0341
- https://ubuntu.com/security/notices/USN-5842-1
- https://github.com/editorconfig/editorconfig-core-c/commit/41281ea82fbf24b060a9f69b9c5369350fb0529e
- https://github.com/editorconfig/editorconfig-core-c/releases
- https://litios.github.io/2023/01/14/CVE-2023-0341.html
