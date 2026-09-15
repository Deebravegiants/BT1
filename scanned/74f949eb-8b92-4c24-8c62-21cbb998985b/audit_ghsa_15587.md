# [H] OpenDaylight Model-Driven Service Abstraction Layer (MD-SAL) allows follower controller to set up flow entries

## Summary
Severity: High
Advisory: GHSA-hv38-h5pj-c96j
CVE: CVE-2024-46942
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-hv38-h5pj-c96j
Type: github-advisory

## Affected
- Maven: `org.opendaylight.mdsal:mdsal-artifacts` — affected >=0

## Details
In OpenDaylight Model-Driven Service Abstraction Layer (MD-SAL) through 13.0.1, a controller with a follower role can configure flow entries in an OpenDaylight clustering deployment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46942
- https://docs.opendaylight.org/en/latest/release-notes/projects/mdsal.html
- https://doi.org/10.48550/arXiv.2408.16940
- https://github.com/opendaylight/mdsal
- https://lf-opendaylight.atlassian.net/browse/MDSAL-869
