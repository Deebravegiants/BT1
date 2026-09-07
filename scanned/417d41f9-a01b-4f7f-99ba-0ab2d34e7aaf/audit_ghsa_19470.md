# [M] Miniflux Media Proxy vulnerable to Stored Cross-site Scripting due to improper Content-Security-Policy configuration

## Summary
Severity: Medium
Advisory: GHSA-cq88-842x-2jhp
CVE: CVE-2025-31483
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-cq88-842x-2jhp
Type: github-advisory

## Affected
- Go: `miniflux.app/v2` — affected >=0 <2.2.7

## Details
## Summary

Due to a weak Content Security Policy on the `/proxy/*` route, an attacker can bypass the CSP of the media proxy and execute cross-site scripting when opening external images in a new tab/window.

## Impact

A malicious feed added to Miniflux can execute arbitrary JavaScript in the user's browser when opening external resources, such as proxified images, in a new tab or window.

## Mitigation

The CSP for the media proxy has been changed from `default-src 'self'` to `default-src 'none'; form-action 'none'; sandbox;`.

Upgrade to Miniflux >= 2.2.7

## Credit
[RyotaK](https://ryotak.net) (GMO Flatt Security Inc.) with [takumi-san.ai](https://takumi-san.ai)

## References
- https://github.com/miniflux/v2/security/advisories/GHSA-cq88-842x-2jhp
- https://nvd.nist.gov/vuln/detail/CVE-2025-31483
- https://github.com/miniflux/v2/commit/cb695e653a08af4cabcb277c271ce74bd0c746e6
- https://github.com/miniflux/v2
