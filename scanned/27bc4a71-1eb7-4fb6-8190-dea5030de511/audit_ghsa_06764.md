# [H] Apollo ConfigService access key authentication bypass via appId parsing and non-canonical matching

## Summary
Severity: High
Advisory: GHSA-4w3q-qpfq-v992
CVE: CVE-2026-59954
CWE: CWE-20, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-4w3q-qpfq-v992
Type: github-advisory

## Affected
- Maven: `com.ctrip.framework.apollo:apollo` — affected >=0

## Details
### Summary
Apollo ConfigService may allow unauthorized access to configuration data when AccessKey / management key authentication is enabled and ConfigService accepts a non-canonical appId variant during authentication while downstream request handling resolves it to the protected app.

### Details
ConfigService extracts appId from configuration and notification requests and uses the extracted value to look up available AccessKey secrets. If the extracted appId is a non-canonical variant that does not exactly match the AccessKey cache key, ConfigService may treat the request as having no available secrets and allow it to continue without signature verification.

This can happen when downstream release lookup still matches the real appId under database collations that treat the values as equivalent. Examples include accent variants under accent-insensitive collations, or trailing-space variants under PAD SPACE collations.

### Impact
An unauthenticated remote attacker may read configuration data from affected ConfigService endpoints when AccessKey / management key authentication is enabled for the target app and the deployment database collation treats a non-canonical appId variant as equivalent to the real appId.

### Affected endpoints
The primary impact is on ConfigService configuration read endpoints under /configs and /configfiles. Notification endpoints using appId parameters are also hardened as defense-in-depth.

### Status
Fixed in Apollo 2.5.2. Users should upgrade to Apollo 2.5.2 or later.

### Related advisory
The raw config file endpoint parsing issue originally described in this advisory has been split into GHSA-h4pc-58cc-hc95 so each independently fixable vulnerability can receive its own CVE.

## References
- https://github.com/apolloconfig/apollo/security/advisories/GHSA-4w3q-qpfq-v992
- https://nvd.nist.gov/vuln/detail/CVE-2026-59954
- https://github.com/apolloconfig/apollo/commit/310809d557e01c6803051736cd525e333ffe00ec
- https://github.com/apolloconfig/apollo
- https://github.com/apolloconfig/apollo/releases/tag/v2.5.2
