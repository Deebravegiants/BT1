# [C] CVE-2019-11929

## Summary
Severity: Critical
Advisory: CVE-2019-11929
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-02
Source: https://osv.dev/vulnerability/CVE-2019-11929
Type: osv

## Details
Insufficient boundary checks when formatting numbers in number_format allows read/write access to out-of-bounds memory, potentially leading to remote code execution. This issue affects HHVM versions prior to 3.30.10, all versions between 4.0.0 and 4.8.5, all versions between 4.9.0 and 4.18.2, and versions 4.19.0, 4.19.1, 4.20.0, 4.20.1, 4.20.2, 4.21.0, 4.22.0, 4.23.0.

## References
- https://hhvm.com/blog/2019/09/25/security-update.html
- https://www.facebook.com/security/advisories/cve-2019-11929
- https://github.com/facebook/hhvm/commit/dbeb9a56a638e3fdcef8b691c2a2967132dae692
