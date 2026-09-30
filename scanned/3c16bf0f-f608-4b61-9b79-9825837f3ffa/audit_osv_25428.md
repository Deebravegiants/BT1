# [M] Mismatched Memory Management Routines in Wireshark

## Summary
Severity: Medium
Advisory: CVE-2023-3648
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-07-14
Source: https://osv.dev/vulnerability/CVE-2023-3648
Type: osv

## Details
Kafka dissector crash in Wireshark 4.0.0 to 4.0.6 and 3.6.0 to 3.6.14 allows denial of service via packet injection or crafted capture file

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00049.html
- https://www.wireshark.org/security/wnpa-sec-2023-21.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3648.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3648
- https://gitlab.com/wireshark/wireshark/-/issues/19105
