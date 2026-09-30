# [H] Buffer Over-read in Wireshark

## Summary
Severity: High
Advisory: CVE-2024-11596
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/CVE-2024-11596
Type: osv

## Details
ECMP dissector crash in Wireshark 4.4.0 to 4.4.1 and 4.2.0 to 4.2.8 allows denial of service via packet injection or crafted capture file

## References
- https://www.wireshark.org/security/wnpa-sec-2024-15.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11596.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11596
- https://gitlab.com/wireshark/wireshark/-/issues/20214
