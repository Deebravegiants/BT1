# [M] Loop with Unreachable Exit Condition ('Infinite Loop') in Wireshark

## Summary
Severity: Medium
Advisory: CVE-2023-4511
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-08-24
Source: https://osv.dev/vulnerability/CVE-2023-4511
Type: osv

## Details
BT SDP dissector infinite loop in Wireshark 4.0.0 to 4.0.7 and 3.6.0 to 3.6.15 allows denial of service via packet injection or crafted capture file

## References
- https://lists.debian.org/debian-lts-announce/2024/02/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00049.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6HCUPLDY7HLPO46PHMGIJSUBJFTT237C/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L4AVRUYSHDNEAJILVSGY5W6MPOMG2YRF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TRKHFQPWFU7F3OXTL6IEIQSJG6FVXZTZ/
- https://www.wireshark.org/security/wnpa-sec-2023-24.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4511.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4511
- https://gitlab.com/wireshark/wireshark/-/issues/19258
