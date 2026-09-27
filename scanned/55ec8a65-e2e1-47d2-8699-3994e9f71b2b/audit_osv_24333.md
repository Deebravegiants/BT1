# [M] Wireshark RTPS Parsing Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2023-0666
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-07
Source: https://osv.dev/vulnerability/CVE-2023-0666
Type: osv

## Details
Due to failure in validating the length provided by an attacker-crafted RTPS packet, Wireshark version 4.0.5 and prior, by default, is susceptible to a heap-based buffer overflow, and possibly code execution in the context of the process running Wireshark.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00049.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0666.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0666
- https://security.gentoo.org/glsa/202309-02
- https://takeonme.org/cves/CVE-2023-0666.html
- https://www.debian.org/security/2023/dsa-5429
- https://www.wireshark.org/docs/relnotes/wireshark-4.0.6.html
- https://www.wireshark.org/security/wnpa-sec-2023-18.html
- https://gitlab.com/wireshark/wireshark/-/issues/19085
