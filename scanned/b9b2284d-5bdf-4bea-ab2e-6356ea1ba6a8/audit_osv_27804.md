# [M] CVE-2024-26306

## Summary
Severity: Medium
Advisory: CVE-2024-26306
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-26306
Type: osv

## Details
iPerf3 before 3.17, when used with OpenSSL before 3.2.0 as a server with RSA authentication, allows a timing side channel in RSA decryption operations. This side channel could be sufficient for an attacker to recover credential plaintext. It requires the attacker to send a large number of messages for decryption, as described in "Everlasting ROBOT: the Marvin Attack" by Hubert Kario.

## References
- https://downloads.es.net/pub/iperf/esnet-secadv-2024-0001.txt.asc
- https://github.com/esnet/iperf/releases/tag/3.17
- https://lists.debian.org/debian-lts-announce/2025/01/msg00027.html
- https://www.insyde.com/security-pledge/SA-2024005
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26306.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26306
- https://security.netapp.com/advisory/ntap-20250228-0007/
