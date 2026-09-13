# [H] Authorization Policy Bypass Due to Case Insensitive Host Comparison

## Summary
Severity: High
Advisory: GHSA-7774-7vr3-cc8j
CVE: CVE-2021-39155
CWE: CWE-178
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-7774-7vr3-cc8j
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=0 <1.9.8
- Go: `istio.io/istio` — affected >=1.10.0 <1.10.4
- Go: `istio.io/istio` — affected >=1.11.0 <1.11.1

## Details
### Impact
According to [RFC 4343](https://datatracker.ietf.org/doc/html/rfc4343), Istio authorization policy should compare the hostname in the HTTP Host header in a case insensitive way, but currently the comparison is case sensitive.  The Envoy proxy will route the request hostname in a case-insensitive way which means the authorization policy could be bypassed.
 
As an example, the user may have an authorization policy that rejects request with hostname "httpbin.foo" for some source IPs, but the attacker can bypass this by sending the request with hostname "Httpbin.Foo".

### Patches
* Istio 1.11.1 and above
* Istio 1.10.4 and above
* Istio 1.9.8 and above

### Workarounds
A Lua filter may be written to normalize Host header before the authorization check.  This is similar to the Path normalization presented in the [Security Best Practices](https://istio.io/latest/docs/ops/best-practices/security/#case-normalization) guide.

### References
More details can be found in the [Istio Security Bulletin](https://istio.io/latest/news/security/istio-security-2021-008).

### For more information
If you have any questions or comments about this advisory, please email us at istio-security-vulnerability-reports@googlegroups.com

## References
- https://github.com/istio/istio/security/advisories/GHSA-7774-7vr3-cc8j
- https://nvd.nist.gov/vuln/detail/CVE-2021-39155
- https://github.com/istio/istio/commit/084b417a486dbe9b9024d4812877016a484572b1
- https://github.com/istio/istio/commit/76ed51413ddd2a7fa253a368ab20a9cec5fb1cbe
- https://github.com/istio/istio/commit/90b00bdf891e6c770cb3235c14a9b1fda96cc7c5
- https://datatracker.ietf.org/doc/html/rfc4343
- https://github.com/istio/istio
