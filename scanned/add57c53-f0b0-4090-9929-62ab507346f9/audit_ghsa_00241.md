# [C] Denial of Service in https-proxy-agent

## Summary
Severity: Critical
Advisory: GHSA-8g7p-74h8-hg48
CVE: CVE-2018-3739
CWE: CWE-125, CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2018-07-27
Source: https://github.com/advisories/GHSA-8g7p-74h8-hg48
Type: github-advisory

## Affected
- npm: `https-proxy-agent` — affected >=0 <2.2.0

## Details
Versions of `https-proxy-agent` before 2.2.0 are vulnerable to denial of service. This is due to unsanitized options (proxy.auth) being passed to `Buffer()`.


## Recommendation

Update to version 2.2.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3736
- https://github.com/TooTallNate/node-https-proxy-agent/commit/1c24219df87524e6ed973127e81f30801d658f07
- https://hackerone.com/reports/319532
- https://github.com/TooTallNate/node-https-proxy-agent
- https://github.com/advisories/GHSA-8g7p-74h8-hg48
- https://www.npmjs.com/advisories/593
