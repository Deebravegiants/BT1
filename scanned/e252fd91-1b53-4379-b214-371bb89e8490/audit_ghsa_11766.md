# [H] Out-of-Bounds Slice Access in free5GC CHF Leading to DoS

## Summary
Severity: High
Advisory: GHSA-6g43-577r-wf4x
CVE: CVE-2026-32937
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-6g43-577r-wf4x
Type: github-advisory

## Affected
- Go: `github.com/free5gc/chf` — affected >=0 <1.2.2

## Details
### Impact
This is an out-of-bounds slice access vulnerability in the CHF `nchf-convergedcharging` service.
A valid authenticated request to PUT `/nchf-convergedcharging/v3/recharging/:ueId?ratingGroup=...` can trigger a server-side panic in `github.com/free5gc/chf/internal/sbi.(*Server).RechargePut(...)` due to an out-of-range slice access. In the reported runtime, Gin recovery converts the panic into HTTP 500, but the recharge path remains remotely panic-triggerable and can be abused repeatedly to degrade recharge functionality and flood logs. In deployments without equivalent recovery handling, this panic may cause more severe service disruption.

### Patches
https://github.com/free5gc/chf/pull/61

### Workarounds
- Restrict access to the `nchf-convergedcharging` recharge endpoint to strictly trusted NF callers only.
- Apply rate limiting or network ACLs in front of the CHF SBI interface to reduce repeated panic-trigger attempts.
- If the recharge API is not required, temporarily disable or block external reachability to this route.
- Ensure panic recovery, monitoring, and alerting are enabled.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-6g43-577r-wf4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-32937
- https://github.com/free5gc/free5gc/issues/864
- https://github.com/free5gc/chf/pull/61
- https://github.com/free5gc/chf/commit/55af766f321a00afa978e806548c96f8a7d2433e
- https://github.com/free5gc/chf
