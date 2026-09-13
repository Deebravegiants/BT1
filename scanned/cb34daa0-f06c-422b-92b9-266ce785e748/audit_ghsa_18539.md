# [M] n8n Vulnerable to Denial of Service via Malformed Binary Data Requests

## Summary
Severity: Medium
Advisory: GHSA-pr9r-gxgp-9rm8
CVE: CVE-2025-49595
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-03
Source: https://github.com/advisories/GHSA-pr9r-gxgp-9rm8
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.99.0

## Details
## Summary
Denial of Service vulnerability in `/rest/binary-data` endpoint when processing empty filesystem URIs (`filesystem://` or `filesystem-v2://`).

### Impact
This is a Denial of Service (DoS) vulnerability that allows authenticated attackers to cause service unavailability through malformed filesystem URI requests. The vulnerability affects:

- The `/rest/binary-data` endpoint
- n8n.cloud instances (confirmed HTTP/2 524 timeout responses)

Attackers can exploit this by sending GET requests with empty filesystem URIs (`filesystem://` or `filesystem-v2://`) to the `/rest/binary-data` endpoint, causing resource exhaustion and service disruption.

### Patches

The issue has been patched in [1.99.0](https://github.com/n8n-io/n8n/releases/tag/n8n%401.99.0).
All users should upgrade to this version or later.

The fix introduces strict checking of URI patterns.

Patch commit: https://github.com/n8n-io/n8n/pull/16229

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-pr9r-gxgp-9rm8
- https://nvd.nist.gov/vuln/detail/CVE-2025-49595
- https://github.com/n8n-io/n8n/pull/16229
- https://github.com/n8n-io/n8n/commit/43c52a8b4f844e91b02e3cc9df92826a2d7b6052
- https://github.com/n8n-io/n8n
