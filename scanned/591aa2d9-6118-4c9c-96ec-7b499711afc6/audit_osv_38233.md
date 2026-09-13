# [M] Papra Does Not Reject Expired API Keys

## Summary
Severity: Medium
Advisory: CVE-2026-35462
Aliases: GHSA-866c-mc22-wvv5
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35462
Type: osv

## Details
Papra is a minimalistic document management and archiving platform. Prior to 26.4.0, API keys with an expiresAt date are never validated against the current time during authentication. Any API key — regardless of its expiration date — is accepted indefinitely, allowing a user whose key has expired to continue accessing all protected endpoints as if the key were still valid. This vulnerability is fixed in 26.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35462.json
- https://github.com/papra-hq/papra/security/advisories/GHSA-866c-mc22-wvv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-35462
