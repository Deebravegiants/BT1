# [H] free5GC NRF Discovery EncodeGroupId Function Panics on Malformed group-id-list Parameter

## Summary
Severity: High
Advisory: GHSA-7c47-xr7q-p6hg
CVE: CVE-2026-33062
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-7c47-xr7q-p6hg
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nrf` — affected >=0 <1.4.2

## Details
**Impact**  
This is an Improper Input Validation vulnerability leading to Denial of Service.  
- **Security Impact**: A remote attacker can cause the NRF service to panic and crash by sending a crafted HTTP GET request with a malformed `group-id-list` parameter. This results in complete denial of service for the NRF discovery service.  
- **Functional Impact**: The `EncodeGroupId` function attempts to access array indices [0], [1], [2] without validating the length of the split data. When the parameter contains insufficient separator characters, the code panics with "index out of range".  
- **Affected Parties**: All deployments of free5GC v4.0.1 using the NRF discovery service.

**Patches**  
Yes, the issue has been patched.  
The fix is implemented in PR free5gc/nrf#80 (commit: [add fix reference here]).  
Users should upgrade to the next release of free5GC that includes this commit.

**Workarounds**  
There is no direct workaround at the application level. The recommendation is to apply the provided patch or restrict access to the NRF API to trusted sources only.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-7c47-xr7q-p6hg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33062
- https://github.com/free5gc/free5gc/issues/777
- https://github.com/free5gc/nrf/pull/80
- https://github.com/free5gc/nrf/commit/dac77d8f8f2e0f041c5634fb3c685dcb9734b872
- https://github.com/free5gc/free5gc
