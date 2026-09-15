# [H] free5GC AUSF UE Authentication Panic on Nil SuciSupiMap Interface Conversion

## Summary
Severity: High
Advisory: GHSA-4jrw-92fg-4jwx
CVE: CVE-2026-33063
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-4jrw-92fg-4jwx
Type: github-advisory

## Affected
- Go: `github.com/free5gc/ausf` — affected >=0 <1.4.2

## Details
**Impact**  
This is an Improper Null Check vulnerability leading to Denial of Service.  
- **Security Impact**: A remote attacker can cause the AUSF service to panic and crash by sending a crafted UE authentication request that triggers a nil interface conversion in the `GetSupiFromSuciSupiMap` function. This results in complete denial of service for the AUSF authentication service.  
- **Functional Impact**: The `GetSupiFromSuciSupiMap` function attempts to perform an interface conversion from `interface{}` to `*context.SuciSupiMap` without checking if the underlying value is nil. When `SuciSupiMap` is nil, the code panics with "interface conversion: interface {} is nil, not *context.SuciSupiMap".  
- **Affected Parties**: All deployments of free5GC v4.0.1 using the AUSF UE authentication service (`/nausf-auth/v1/ue-authentications` endpoint).

**Patches**  
Yes, the issue has been patched.  
The fix is implemented in PR free5gc/ausf#52 (commit: [add specific commit hash if available]).  
Users should upgrade to the next release of free5GC that includes this commit.

**Workarounds**  
There is no direct workaround at the application level. The recommendation is to apply the provided patch or restrict access to the AUSF API to trusted sources only.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-4jrw-92fg-4jwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33063
- https://github.com/free5gc/free5gc/issues/778
- https://github.com/free5gc/ausf/pull/52
- https://github.com/free5gc/ausf/commit/3b9ac4403c2756dc89a5ed3cdcefe688458588aa
- https://github.com/free5gc/free5gc
