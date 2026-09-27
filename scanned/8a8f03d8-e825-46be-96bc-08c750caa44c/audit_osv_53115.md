# [M] CVE-2022-29901

## Summary
Severity: Medium
Advisory: CVE-2022-29901
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-07-12
Source: https://osv.dev/vulnerability/CVE-2022-29901
Type: osv

## Details
Intel microprocessor generations 6 to 8 are affected by a new Spectre variant that is able to bypass their retpoline mitigation in the kernel to leak arbitrary data. An attacker with unprivileged user access can hijack return instructions to achieve arbitrary speculative code execution under certain microarchitecture-dependent conditions.

## References
- http://www.openwall.com/lists/oss-security/2022/07/12/5
- https://lists.debian.org/debian-lts-announce/2022/09/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D4RW5FCIYFNCQOEFJEUIRW3DGYW7CWBG/
- http://www.openwall.com/lists/oss-security/2022/07/12/2
- http://www.openwall.com/lists/oss-security/2022/07/12/4
- http://www.openwall.com/lists/oss-security/2022/07/13/1
- https://comsec.ethz.ch/retbleed
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M27MB3QFNIJV4EQQSXWARHP3OGX6CR6K/
- https://www.debian.org/security/2022/dsa-5207
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00702.html
- https://security.gentoo.org/glsa/202402-07
- https://security.netapp.com/advisory/ntap-20221007-0007/
- https://www.secpod.com/blog/retbleed-intel-and-amd-processor-information-disclosure-vulnerability/
