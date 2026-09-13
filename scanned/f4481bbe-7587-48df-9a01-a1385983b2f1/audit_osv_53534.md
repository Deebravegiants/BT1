# [H] CVE-2022-47630

## Summary
Severity: High
Advisory: CVE-2022-47630
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-01-16
Source: https://osv.dev/vulnerability/CVE-2022-47630
Type: osv

## Details
Trusted Firmware-A through 2.8 has an out-of-bounds read in the X.509 parser for parsing boot certificates. This affects downstream use of get_ext and auth_nvctr. Attackers might be able to trigger dangerous read side effects or obtain sensitive information about microarchitectural state.

## References
- https://www.trustedfirmware.org/news/
- http://www.openwall.com/lists/oss-security/2023/01/16/8
- https://trustedfirmware-a.readthedocs.io/en/latest/security_advisories/security-advisory-tfv-10.html
