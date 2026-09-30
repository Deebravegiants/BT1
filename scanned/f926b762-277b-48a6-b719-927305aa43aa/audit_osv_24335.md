# [M] Wireshark IEEE-C37.118 parsing buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2023-0668
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-07
Source: https://osv.dev/vulnerability/CVE-2023-0668
Type: osv

## Details
Due to failure in validating the length provided by an attacker-crafted IEEE-C37.118 packet, Wireshark version 4.0.5 and prior, by default, is susceptible to a heap-based buffer overflow, and possibly code execution in the context of the process running Wireshark.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00049.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0668.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0668
- https://security.gentoo.org/glsa/202309-02
- https://takeonme.org/cves/CVE-2023-0668.html
- https://www.debian.org/security/2023/dsa-5429
- https://www.wireshark.org/docs/relnotes/wireshark-4.0.6.html
- https://www.wireshark.org/security/wnpa-sec-2023-19.html
- https://gitlab.com/wireshark/wireshark/-/issues/19087
