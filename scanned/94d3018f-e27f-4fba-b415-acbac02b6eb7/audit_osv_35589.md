# [M] Nexus Repository Manager - Incorrect Authorization allows credential disclosure via proxy repository configuration

## Summary
Severity: Medium
Advisory: CVE-2026-10741
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-10741
Type: osv

## Details
Sonatype Nexus Repository Manager before 3.93.0 contains an authorization vulnerability in the proxy repository configuration that allows a delegated repository administrator to disclose stored upstream proxy credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10741.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10741
- https://support.sonatype.com/hc/en-us/articles/52341191736851
- https://help.sonatype.com/en/sonatype-nexus-repository-3-93-0-release-notes.html
