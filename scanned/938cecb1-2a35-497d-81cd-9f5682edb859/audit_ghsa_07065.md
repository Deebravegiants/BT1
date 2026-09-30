# [H] Apollo ConfigService access key authentication bypass via raw config file appId parsing

## Summary
Severity: High
Advisory: GHSA-h4pc-58cc-hc95
CVE: CVE-2026-59955
CWE: CWE-20, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-h4pc-58cc-hc95
Type: github-advisory

## Affected
- Maven: `com.ctrip.framework.apollo:apollo` — affected >=0

## Details
### Summary
Apollo ConfigService may allow unauthorized access to raw configuration data when AccessKey / management key authentication is enabled because authentication parsed the appId incorrectly for the raw config file endpoint.

### Details
Requests under /configfiles/raw/{appId}/{clusterName}/{namespace} were parsed for authentication as appId "raw" instead of the actual path appId. ConfigService used the parsed appId to look up available AccessKey secrets before verifying the request signature.

If no AccessKey is configured for an application literally named "raw", ConfigService may treat the request as having no available secrets and allow it to continue without signature verification, even when AccessKey / management key authentication is enabled for the actual target appId in the path.

### Impact
An unauthenticated remote attacker may read raw configuration data from affected ConfigService endpoints when AccessKey / management key authentication is enabled for the target app and the attacker requests the raw config file endpoint.

### Affected endpoints
The primary impact is on ConfigService raw config file reads under /configfiles/raw/{appId}/{clusterName}/{namespace}.

### Status
Fixed in Apollo 2.5.2. Users should upgrade to Apollo 2.5.2 or later.

### Related advisory
The non-canonical appId matching issue is tracked separately in GHSA-4w3q-qpfq-v992 so each independently fixable vulnerability can receive its own CVE.

## References
- https://github.com/apolloconfig/apollo/security/advisories/GHSA-h4pc-58cc-hc95
- https://nvd.nist.gov/vuln/detail/CVE-2026-59955
- https://github.com/apolloconfig/apollo/commit/310809d557e01c6803051736cd525e333ffe00ec
- https://github.com/apolloconfig/apollo
- https://github.com/apolloconfig/apollo/releases/tag/v2.5.2
