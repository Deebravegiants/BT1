# [H] Uncontrolled Recursion in Wireshark

## Summary
Severity: High
Advisory: CVE-2025-1492
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-20
Source: https://osv.dev/vulnerability/CVE-2025-1492
Type: osv

## Details
Bundle Protocol and CBOR dissector crashes in Wireshark 4.4.0 to 4.4.3 and 4.2.0 to 4.2.10 allows denial of service via packet injection or crafted capture file

## References
- https://www.wireshark.org/security/wnpa-sec-2025-01.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1492.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1492
- https://gitlab.com/wireshark/wireshark/-/issues/20373
