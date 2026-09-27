# [H] Expired Pointer Dereference in Wireshark

## Summary
Severity: High
Advisory: CVE-2024-8250
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-08-28
Source: https://osv.dev/vulnerability/CVE-2024-8250
Type: osv

## Details
NTLMSSP dissector crash in Wireshark 4.2.0 to 4.0.6 and 4.0.0 to 4.0.16 allows denial of service via packet injection or crafted capture file

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00049.html
- https://www.wireshark.org/security/wnpa-sec-2024-11.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8250.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8250
- https://gitlab.com/wireshark/wireshark/-/issues/19943
