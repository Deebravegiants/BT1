# [H] Istio may not check inbound TCP connections against istio-policy

## Summary
Severity: High
Advisory: GHSA-6g5f-f5pm-mjrg
CVE: CVE-2019-12243
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N/E:H/RL:O/RC:C (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-6g5f-f5pm-mjrg
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=1.1.0 <1.1.7

## Details
Istio 1.1.x through 1.1.6 has Incorrect Access Control. When `disablePolicyChecks` is set to `false`, inbound TCP connections do not generate Check requests to istio-policy and external authorization is not applied.

This behavior is a result of a change to `istio/pilot/pkg/networking/plugin/mixer/mixer.go` in 1.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12243
- https://github.com/istio/istio/issues/13868
- https://github.com/istio/istio/pull/13893/commits/91faba277439dab798185730d1624bd53e37bb06
- https://istio.io/blog/2019/cve-2019-12243
