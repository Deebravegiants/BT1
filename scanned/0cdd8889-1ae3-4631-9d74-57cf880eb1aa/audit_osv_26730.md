# [M] Memory Allocation with Excessive Size Value in Wireshark

## Summary
Severity: Medium
Advisory: CVE-2023-5371
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-5371
Type: osv

## Details
RTPS dissector memory leak in Wireshark 4.0.0 to 4.0.8 and 3.6.0 to 3.6.16 allows denial of service via packet injection or crafted capture file

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/34DBP5P2RHQ7XUABPANYYMOGV5KS6VEP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MADSCHKZSCKQ5NLIX3UMOIJD2JZ65L4V/
- https://www.wireshark.org/security/wnpa-sec-2023-27.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5371.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5371
- https://security.gentoo.org/glsa/202402-09
- https://gitlab.com/wireshark/wireshark/-/issues/19322
