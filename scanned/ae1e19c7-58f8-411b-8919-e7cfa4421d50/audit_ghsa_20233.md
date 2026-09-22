# [M] Ill-formed headers may lead to unexpected behavior in Istio

## Summary
Severity: Medium
Advisory: GHSA-xwx5-5c9g-x68x
CVE: CVE-2022-31045
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-10
Source: https://github.com/advisories/GHSA-xwx5-5c9g-x68x
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=0 <1.12.18
- Go: `istio.io/istio` — affected >=1.13.0 <1.13.5
- Go: `istio.io/istio` — affected >=1.14.0 <1.14.1

## Details
### Impact
Ill-formed headers sent to Envoy in certain configurations can lead to unexpected memory access resulting in undefined behavior or crashing.

You are at most risk if you have an Istio ingress Gateway exposed to external traffic.

### Patches
1.12.8, 1.13.5, 1.14.1

### Workarounds
No.

### References
More details can be found in the [Istio Security Bulletin](https://istio.io/latest/news/security/istio-security-2022-05)

### For more information
If you have any questions or comments about this advisory, please email us at [istio-security-vulnerability-reports@googlegroups.com](mailto:istio-security-vulnerability-reports@googlegroups.com)

## References
- https://github.com/istio/istio/security/advisories/GHSA-xwx5-5c9g-x68x
- https://nvd.nist.gov/vuln/detail/CVE-2022-31045
- https://github.com/istio/istio
- https://istio.io/latest/news/security/istio-security-2022-05
