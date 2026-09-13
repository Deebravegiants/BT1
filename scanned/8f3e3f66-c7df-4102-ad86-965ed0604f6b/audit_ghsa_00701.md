# [M] Insufficient Entropy in Spring Security

## Summary
Severity: Medium
Advisory: GHSA-2ppp-9496-p23q
CVE: CVE-2020-5408
CWE: CWE-329, CWE-330
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-2ppp-9496-p23q
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=5.3.0 <5.3.2
- Maven: `org.springframework.security:spring-security-core` — affected >=5.2.0 <5.2.4
- Maven: `org.springframework.security:spring-security-core` — affected >=5.1.0 <5.1.10
- Maven: `org.springframework.security:spring-security-core` — affected >=5.0.0 <5.0.16
- Maven: `org.springframework.security:spring-security-core` — affected >=0 <4.2.16

## Details
Spring Security versions 5.3.x prior to 5.3.2, 5.2.x prior to 5.2.4, 5.1.x prior to 5.1.10, 5.0.x prior to 5.0.16 and 4.2.x prior to 4.2.16 use a fixed null initialization vector with CBC Mode in the implementation of the queryable text encryptor. A malicious user with access to the data that has been encrypted using such an encryptor may be able to derive the unencrypted values using a dictionary attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5408
- https://tanzu.vmware.com/security/cve-2020-5408
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
