# [H] Istio Fragments in Path May Lead to Authorization Policy Bypass

## Summary
Severity: High
Advisory: GHSA-hqxw-mm44-gc4r
CVE: CVE-2021-39156
CWE: CWE-706, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-hqxw-mm44-gc4r
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=0 <1.9.8
- Go: `istio.io/istio` — affected >=1.10.0 <1.10.4
- Go: `istio.io/istio` — affected >=1.11.0 <1.11.1

## Details
### Impact
Istio 1.11.0, 1.10.3 and below, and 1.9.7 and below contain a remotely exploitable vulnerability where an HTTP request with `#fragment` in the path may bypass Istio’s URI path based authorization policies. 

### Patches
* Istio 1.11.1 and above
* Istio 1.10.4 and above
* Istio 1.9.8 and above

### Workarounds
A Lua filter may be written to normalize the path.  This is similar to the Path normalization presented in the [Security Best Practices](https://istio.io/latest/docs/ops/best-practices/security/#case-normalization) guide.

### References
More details can be found in the [Istio Security Bulletin](https://istio.io/latest/news/security/istio-security-2021-008)

### For more information
If you have any questions or comments about this advisory, please email us at istio-security-vulnerability-reports@googlegroups.com

## References
- https://github.com/istio/istio/security/advisories/GHSA-hqxw-mm44-gc4r
- https://nvd.nist.gov/vuln/detail/CVE-2021-39156
- https://github.com/istio/istio
- https://istio.io/latest/news/security/istio-security-2021-008
