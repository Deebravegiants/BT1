# [H] Payload has Authenticated SSRF via Upload Functionality

## Summary
Severity: High
Advisory: GHSA-6r7f-q7f5-wpx8
CVE: CVE-2026-34746
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-6r7f-q7f5-wpx8
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <3.79.1

## Details
### Impact

An authenticated Server-Side Request Forgery (SSRF) vulnerability existed in the upload functionality.

Authenticated users with `create` or `update` access to an upload-enabled collection could cause the server to make outbound HTTP requests to arbitrary URLs.

Consumers are affected if ALL of these are true:

- Payload version **< v3.79.1**
- At least one collection with `upload` enabled
- An authenticated user has `create` or `update` access to that collection

### Patches

This vulnerability has been patched in **v3.79.1**. Users should upgrade to **v3.79.1** or later.

### Workarounds

Until consumers can upgrade:

- Restrict `create` and `update` access to upload-enabled collections to trusted roles only.
- Limit outbound network access from your Payload server where possible.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-6r7f-q7f5-wpx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-34746
- https://github.com/payloadcms/payload
- https://github.com/payloadcms/payload/releases/tag/v3.79.1
