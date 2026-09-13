# [H] NULL Pointer Dereference in Wireshark

## Summary
Severity: High
Advisory: CVE-2024-0209
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-03
Source: https://osv.dev/vulnerability/CVE-2024-0209
Type: osv

## Details
IEEE 1609.2 dissector crash in Wireshark 4.2.0, 4.0.0 to 4.0.11, and 3.6.0 to 3.6.19 allows denial of service via packet injection or crafted capture file

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00049.html
- https://www.wireshark.org/security/wnpa-sec-2024-02.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0209.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0209
- https://gitlab.com/wireshark/wireshark/-/issues/19501
