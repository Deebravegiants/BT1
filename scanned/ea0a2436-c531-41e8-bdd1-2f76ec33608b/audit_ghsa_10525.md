# [M] OpenFGA: Unauthenticated playground endpoint discloses preshared API key in HTML response

## Summary
Severity: Medium
Advisory: GHSA-68m9-983m-f3v5
CVE: CVE-2026-40293
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-68m9-983m-f3v5
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0.1.4 <1.14.0

## Details
### Description
When OpenFGA is configured to use preshared-key authentication with the built-in playground enabled, the local server includes the preshared API key in the HTML response of the /playground endpoint. The /playground endpoint is enabled by default and does not require authentication. It is intended for local development and debugging and is not designed to be exposed to production environments.


### Am I Affected?
You are affected if you meet each of the following preconditions:
* You are running OpenFGA with --authn-method preshared, and
* The playground is enabled, and
* The playground endpoint is accessible beyond localhost or trusted networks.

### Fix
Upgrade to OpenFGA v1.14.0, or disable the playground by running `./openfga run --playground-enabled=false.`

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-68m9-983m-f3v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-40293
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v1.14.0
