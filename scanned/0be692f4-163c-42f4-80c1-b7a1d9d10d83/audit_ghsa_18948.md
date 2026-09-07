# [M] kgateway is missing xDS authorization

## Summary
Severity: Medium
Advisory: GHSA-4766-x535-jw3r
CVE: CVE-2025-64323
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-04
Source: https://github.com/advisories/GHSA-4766-x535-jw3r
Type: github-advisory

## Affected
- Go: `github.com/kgateway-dev/kgateway/v2` — affected >=2.1.0-agw-cel-rbac <2.1.0
- Go: `github.com/kgateway-dev/kgateway/v2` — affected >=0 <2.0.5

## Details
## Summary

The xDS interface in Kgateway versions 2.0.0 through 2.0.4 lacks authentication, allowing any client with unrestricted network access to the xDS port to retrieve potentially sensitive configuration data including certificate data, backend service information, routing rules, and cluster metadata.

## Description

### Impact

Kgateway xDS interface did not have authorization, so anonymous clients with unrestricted network access could gain access to the xDS data. This could expose sensitive information about your gateway configuration, certificate data, backend services, and routing topology to unauthorized parties.

### Patches

Upgrade to version 2.0.5 or 2.1.0. These versions enable JWT-based authentication for the xDS interface by default, ensuring that only authenticated clients can access the xDS configuration data.

### Workarounds

If immediate upgrade is not possible, NetworkPolicies can be used to block access to kgateway's xDS port, restricting network access to only trusted sources.

## References

- Fix in 2.1.0: https://github.com/kgateway-dev/kgateway/pull/12471
- Backport to 2.0.5: https://github.com/kgateway-dev/kgateway/pull/12535
- Related issue: https://github.com/kgateway-dev/kgateway/issues/10651

## Credits

Kindly reported by @rikatz

## For More Information

If you have any questions or comments about this advisory, please reach out in slack https://cloud-native.slack.com/archives/C080D3PJMS4

## References
- https://github.com/kgateway-dev/kgateway/security/advisories/GHSA-4766-x535-jw3r
- https://nvd.nist.gov/vuln/detail/CVE-2025-64323
- https://github.com/kgateway-dev/kgateway/issues/10651
- https://github.com/kgateway-dev/kgateway/pull/12471
- https://github.com/kgateway-dev/kgateway/pull/12535
- https://github.com/kgateway-dev/kgateway
