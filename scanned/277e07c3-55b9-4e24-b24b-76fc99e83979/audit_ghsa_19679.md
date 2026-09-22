# [H] H2O Vulnerable to Denial of Service (DoS) via `/3/ParseSetup` Endpoint

## Summary
Severity: High
Advisory: GHSA-7qq7-pvm9-x8rf
CVE: CVE-2024-10550
CWE: CWE-1333
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-7qq7-pvm9-x8rf
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=3.30.0.7
- Maven: `ai.h2o:h2o-core` — affected >=3.30.0.7

## Details
A vulnerability in the `/3/ParseSetup` endpoint of h2oai/h2o-3 version 3.46.0.1 allows for a denial of service (DoS) attack. The endpoint applies a user-specified regular expression to a user-controllable string. This can be exploited by an attacker to cause inefficient regular expression complexity, leading to the exhaustion of server resources and making the server unresponsive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10550
- https://github.com/h2oai/h2o-3
- https://github.com/h2oai/h2o-3/blob/51c25940ded8b7d0acc8f3f72329fd9dedbb3a34/h2o-core/src/main/java/water/api/ParseSetupHandler.java#L121
- https://huntr.com/bounties/ef3f4d89-3b8b-4618-b134-cb93c1664ec6
