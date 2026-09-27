# [H] CVE-2022-41859

## Summary
Severity: High
Advisory: CVE-2022-41859
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2022-41859
Type: osv

## Details
In freeradius, the EAP-PWD function compute_password_element() leaks information about the password which allows an attacker to substantially reduce the size of an offline dictionary attack.

## References
- https://freeradius.org/security/
- https://lists.debian.org/debian-lts-announce/2025/06/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41859.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41859
- https://github.com/FreeRADIUS/freeradius-server/commit/9e5e8f2f
