# [H] Istio ReDoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-qcvw-82hh-gq38
CVE: CVE-2019-14993
CWE: CWE-185
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qcvw-82hh-gq38
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=0 <1.1.13
- Go: `istio.io/istio` — affected >=1.2.0 <1.2.4

## Details
Istio before 1.1.13 and 1.2.x before 1.2.4 mishandles regular expressions for long URIs, leading to a denial of service during use of the JWT, VirtualService, HTTPAPISpecBinding, or QuotaSpecBinding API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14993
- https://github.com/envoyproxy/envoy/issues/7728
- https://discuss.istio.io/t/upcoming-security-updates-in-istio-1-2-4-and-1-1-13/3383
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=86164
- https://istio.io/blog/2019/istio-security-003-004
