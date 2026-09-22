# [M] Smokescreen SSRF via deny list bypass (square brackets)

## Summary
Severity: Medium
Advisory: GHSA-qwrf-gfpj-qvj6
CVE: CVE-2022-29188
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qwrf-gfpj-qvj6
Type: github-advisory

## Affected
- Go: `github.com/stripe/smokescreen` — affected >=0 <0.0.4

## Details
### Impact
The primary use case for Smokescreen is to prevent server-side request forgery (SSRF) attacks in which external attackers leverage the behavior of applications to connect to or scan internal infrastructure.

Smokescreen also offers an option to deny access to additional (e.g., external) URLs by way of a deny list. There was an issue in Smokescreen that made it possible to bypass the deny list feature by surrounding the hostname with square brackets (e.g. `[example.com]`). 

### Recommendation
Upgrade Smokescreen to version 0.0.4 or later.

### Acknowledgements
Thanks to [Axel Chong](https://github.com/haxatron) for reporting the issue.

### For more information
Email us at security@stripe.com

## References
- https://github.com/stripe/smokescreen/security/advisories/GHSA-qwrf-gfpj-qvj6
- https://nvd.nist.gov/vuln/detail/CVE-2022-29188
- https://github.com/stripe/smokescreen/commit/dea7b3c89df000f4072ff9866d61d78e30df6a36
- github.com/stripe/smokescreen
