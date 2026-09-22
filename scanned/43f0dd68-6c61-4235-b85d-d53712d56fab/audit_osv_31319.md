# [M] Access of Uninitialized Pointer in Wireshark

## Summary
Severity: Medium
Advisory: CVE-2024-8645
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-09-10
Source: https://osv.dev/vulnerability/CVE-2024-8645
Type: osv

## Details
SPRT dissector crash in Wireshark 4.2.0 to 4.0.5 and 4.0.0 to 4.0.15 allows denial of service via packet injection or crafted capture file

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00049.html
- https://www.wireshark.org/security/wnpa-sec-2024-10.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8645.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8645
- https://gitlab.com/wireshark/wireshark/-/issues/19559
