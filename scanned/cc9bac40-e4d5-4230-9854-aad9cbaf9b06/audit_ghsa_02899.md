# [M] Insufficient Granularity of Access Control in github.com/google/exposure-notifications-verification-server

## Summary
Severity: Medium
Advisory: GHSA-wx8q-rgfr-cf6v
CVE: CVE-2021-22565
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-wx8q-rgfr-cf6v
Type: github-advisory

## Affected
- Go: `github.com/google/exposure-notifications-verification-server` — affected >=0 <1.1.2

## Details
### Impact
Users or API keys with permission to expire verification codes could have expired codes that belonged to another realm if they guessed the UUID.

### Patches
v1.1.2+

### Workarounds
There are no workarounds, and there are no indications this has been exploited in the wild. Verification codes can only be expired by providing their 64-bit UUID, and verification codes are already valid for a very short period of time (thus the UUID rotates frequently).

### For more information
Contact exposure-notifications-feedback@google.com

## References
- https://github.com/google/exposure-notifications-verification-server/security/advisories/GHSA-wx8q-rgfr-cf6v
- https://nvd.nist.gov/vuln/detail/CVE-2021-22565
- https://github.com/google/exposure-notifications-verification-server
- https://github.com/google/exposure-notifications-verification-server/releases/tag/v1.1.2
