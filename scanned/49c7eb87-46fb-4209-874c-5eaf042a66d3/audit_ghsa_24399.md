# [H] Istio vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-vc7h-cmp3-4hw5
CVE: CVE-2019-18817
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vc7h-cmp3-4hw5
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=1.3.0 <1.3.5

## Details
Istio 1.3.x before 1.3.5 is vulnerable to denial of service because `continue_on_listener_filters_timeout` is set to True, a related issue to CVE-2019-18836.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18817
- https://github.com/istio/istio/issues/18229
- https://github.com/istio/istio/issues/18229#issuecomment-553190142
- https://github.com/istio/istio/commit/7570a1f5b56c108aed6ecfa5d2a6048f444bfb37
- https://github.com/istio/istio
- https://istio.io/news/2019/announcing-1.3.5
