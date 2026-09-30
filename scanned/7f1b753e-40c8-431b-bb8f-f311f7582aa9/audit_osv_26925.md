# [H] Buffer Copy without Checking Size of Input ('Classic Buffer Overflow') in Wireshark

## Summary
Severity: High
Advisory: CVE-2023-6175
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2023-6175
Type: osv

## Details
NetScreen file parser crash in Wireshark 4.0.0 to 4.0.10 and 3.6.0 to 3.6.18 allows denial of service via crafted capture file

## References
- https://lists.debian.org/debian-lts-announce/2024/02/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00049.html
- https://www.wireshark.org/security/wnpa-sec-2023-29.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6175.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6175
- https://gitlab.com/wireshark/wireshark/-/issues/19404
