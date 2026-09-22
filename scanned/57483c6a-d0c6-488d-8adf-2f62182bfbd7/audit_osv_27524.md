# [M] CVE-2024-23170

## Summary
Severity: Medium
Advisory: CVE-2024-23170
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/CVE-2024-23170
Type: osv

## Details
An issue was discovered in Mbed TLS 2.x before 2.28.7 and 3.x before 3.5.2. There was a timing side channel in RSA private operations. This side channel could be sufficient for a local attacker to recover the plaintext. It requires the attacker to send a large number of messages for decryption, as described in "Everlasting ROBOT: the Marvin Attack" by Hubert Kario.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GP5UU7Z6LJNBLBT4SC5WWS2HDNMTFZH5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IIBPEYSVRK4IFLBSYJAWKH33YBNH5HR2/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23170.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GP5UU7Z6LJNBLBT4SC5WWS2HDNMTFZH5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IIBPEYSVRK4IFLBSYJAWKH33YBNH5HR2/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2024-01-1/
- https://nvd.nist.gov/vuln/detail/CVE-2024-23170
