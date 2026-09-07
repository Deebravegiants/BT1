# [M] ExpressGateway Cross-Site Scripting Vulnerability in lib/rest/routes/apps.js

## Summary
Severity: Medium
Advisory: GHSA-xfp8-x3j6-h67v
CVE: CVE-2025-9096
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-08-18
Source: https://github.com/advisories/GHSA-xfp8-x3j6-h67v
Type: github-advisory

## Affected
- npm: `express-gateway` — affected >=0

## Details
A cross-site scripting (XSS) issue exists in ExpressGateway ≤ 1.16.10 in lib/rest/routes/apps.js. User-controlled data returned by the REST endpoint is not sanitized before being rendered by the admin/UI layer, allowing an authenticated, low-privileged actor to store or reflect a payload that executes in a maintainer’s browser when the resource is viewed. The issue can be triggered remotely over the network and does not impact availability. No vendor fix is available at this time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9096
- https://github.com/freshfish-hust/my-cves/issues/6
- https://github.com/freshfish-hust/my-cves/issues/6#issue-3287078206
- https://github.com/ExpressGateway/express-gateway
- https://vuldb.com/?ctiid.320418
- https://vuldb.com/?id.320418
- https://vuldb.com/?submit.627833
