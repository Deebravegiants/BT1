# [M] Privilege Context Switching Error in wildlfy

## Summary
Severity: Medium
Advisory: GHSA-p9cf-qjxq-vxw6
CVE: CVE-2020-1719
CWE: CWE-270
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-p9cf-qjxq-vxw6
Type: github-advisory

## Affected
- Maven: `org.wildfly.bom:wildfly` — affected >=0 <20.0.0.Final

## Details
A flaw was found in wildfly. The EJBContext principle is not popped back after invoking another EJB using a different Security Domain. The highest threat from this vulnerability is to data confidentiality and integrity. Versions before wildfly 20.0.0.Final are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1719
- https://bugzilla.redhat.com/show_bug.cgi?id=1796617
