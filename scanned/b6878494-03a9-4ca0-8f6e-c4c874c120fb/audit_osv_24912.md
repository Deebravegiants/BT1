# [H] CVE-2023-28366

## Summary
Severity: High
Advisory: CVE-2023-28366
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-01
Source: https://osv.dev/vulnerability/CVE-2023-28366
Type: osv

## Details
The broker in Eclipse Mosquitto 1.3.2 through 2.x before 2.0.16 has a memory leak that can be abused remotely when a client sends many QoS 2 messages with duplicate message IDs, and fails to respond to PUBREC commands. This occurs because of mishandling of EAGAIN from the libc send function.

## References
- https://github.com/eclipse/mosquitto/compare/v2.0.15...v2.0.16
- https://www.compass-security.com/fileadmin/Research/Advisories/2023_02_CSNC-2023-001_Eclipse_Mosquitto_Memory_Leak.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28366.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KJ2FMBGVVQEQWTTQB7YLKTAHMX2UM66X/
- https://nvd.nist.gov/vuln/detail/CVE-2023-28366
- https://security.gentoo.org/glsa/202401-09
- https://www.debian.org/security/2023/dsa-5511
- https://github.com/eclipse/mosquitto/commit/6113eac95a9df634fbc858be542c4a0456bfe7b9
- https://mosquitto.org/blog/2023/08/version-2-0-16-released/
