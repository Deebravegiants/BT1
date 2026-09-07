# [M] OpenDaylight Authentication, Authorization and Accounting (AAA) peer impersonation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-46hr-3cq3-mcgp
CVE: CVE-2024-46943
CWE: CWE-285, CWE-287, CWE-520
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-46hr-3cq3-mcgp
Type: github-advisory

## Affected
- Maven: `org.opendaylight.aaa:aaa-artifacts` — affected >=0

## Details
An issue was discovered in OpenDaylight Authentication, Authorization and Accounting (AAA) through 0.19.3. A rogue controller can join a cluster to impersonate an offline peer, even if this rogue controller does not possess the complete cluster configuration information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46943
- https://docs.opendaylight.org/en/latest/release-notes/projects/aaa.html
- https://doi.org/10.48550/arXiv.2408.16940
- https://github.com/opendaylight/aaa
- https://lf-opendaylight.atlassian.net/browse/AAA-285
