# [H] CVE-2022-41860

## Summary
Severity: High
Advisory: CVE-2022-41860
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2022-41860
Type: osv

## Details
In freeradius, when an EAP-SIM supplicant sends an unknown SIM option, the server will try to look that option up in the internal dictionaries. This lookup will fail, but the SIM code will not check for that failure. Instead, it will dereference a NULL pointer, and cause the server to crash.

## References
- https://freeradius.org/security/
- https://lists.debian.org/debian-lts-announce/2025/06/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41860.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41860
- https://github.com/FreeRADIUS/freeradius-server/commit/f1cdbb33ec61c4a64a
