# [H] Istio may allow identity impersonation if user has localhost access

## Summary
Severity: High
Advisory: GHSA-6c6p-h79f-g6p4
CVE: CVE-2022-39388
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-11-09
Source: https://github.com/advisories/GHSA-6c6p-h79f-g6p4
Type: github-advisory

## Affected
- Go: `github.com/istio/istio` — affected >=1.15.0-beta.0 <1.15.3

## Details
### Impact

User can impersonate any workload identity within the service mesh if they have localhost access to the Istiod control plane.

### Patches
1.15.3

### Workarounds
No. If using 1.15.2 please upgrade to 1.15.3 or later.

### References
None at this time.

### For more information
If you have any questions or comments about this advisory, please email us at [istio-security-vulnerability-reports@googlegroups.com](mailto:istio-security-vulnerability-reports@googlegroups.com)

## References
- https://github.com/istio/istio/security/advisories/GHSA-6c6p-h79f-g6p4
- https://nvd.nist.gov/vuln/detail/CVE-2022-39388
- https://github.com/istio/istio/commit/346260e5115e9fbc65ba8a559bc686e6ca046a32
- https://github.com/istio/istio/commit/9a643e270421560afb2630e00f76d46a55499df9
- https://github.com/istio/istio
- https://istio.io/latest/news/releases/1.15.x/announcing-1.15.3
