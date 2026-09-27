# [H] ethyca-fides Webserver API Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-r25m-cr6v-p9hq
CVE: CVE-2023-36827
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-r25m-cr6v-p9hq
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=0 <2.15.1

## Details
### Impact
A path traversal (directory traversal) vulnerability affects fides versions lower than `2.15.1`, allowing remote attackers to access arbitrary files on the fides webserver container's filesystem.

### Patches
The vulnerability is patched in fides `2.15.1`. Users should upgrade to this version.

### Workarounds
If the Fides webserver API is not directly accessible to attackers and is instead deployed behind a reverse proxy as recommended in Ethyca's [security best practice documentation](https://docs.ethyca.com/docs/configuration/security-practices#reverse-proxy), and the reverse proxy is an AWS application load balancer, the vulnerability can't be exploited by these attackers. An AWS application load balancer will reject this attack with a 400 error.

Additionally, any secrets supplied to the container using environment variables rather than a `fides.toml` configuration file are not affected by this vulnerability.

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-r25m-cr6v-p9hq
- https://nvd.nist.gov/vuln/detail/CVE-2023-36827
- https://github.com/ethyca/fides/commit/f526d9ffb176006d701493c9d0eff6b4884e811f
- https://github.com/ethyca/fides
- https://github.com/ethyca/fides/releases/tag/2.15.1
- https://github.com/pypa/advisory-database/tree/main/vulns/ethyca-fides/PYSEC-2023-107.yaml
