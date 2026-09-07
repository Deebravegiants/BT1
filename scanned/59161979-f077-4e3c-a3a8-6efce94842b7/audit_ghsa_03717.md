# [H] rendertron can remotely shut down Chrome instance

## Summary
Severity: High
Advisory: GHSA-4q69-q4q7-x82c
CVE: CVE-2017-18353
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-4q69-q4q7-x82c
Type: github-advisory

## Affected
- npm: `rendertron` — affected >=0 <1.1.0

## Details
Rendertron 1.0.0 includes an `_ah/stop` route to shutdown the Chrome instance responsible for serving render requests to all users. Visiting this route with a GET request allows any unauthorized remote attacker to disable the core service of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18353
- https://github.com/GoogleChrome/rendertron/pull/88
- https://github.com/GoogleChrome/rendertron/commit/8d70628c96ae72eff6eebb451d26fc9ed6b58b0e
- https://bugs.chromium.org/p/chromium/issues/detail?id=759111
- https://github.com/GoogleChrome/rendertron
- https://github.com/advisories/GHSA-4q69-q4q7-x82c
