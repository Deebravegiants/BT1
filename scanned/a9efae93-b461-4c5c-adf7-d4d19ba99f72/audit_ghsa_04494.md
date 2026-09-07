# [M] NocoDB: Open Redirect via Hash Fragment in hashRedirect Plugin

## Summary
Severity: Medium
Advisory: GHSA-rvp5-9p55-f5rp
CVE: CVE-2026-47377
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-rvp5-9p55-f5rp
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.04.1

## Details
### Summary

The client-side `hashRedirect` plugin called `window.location.replace()` on a path extracted from the URL hash fragment after only checking `hashPath.startsWith('/')`. Protocol-relative URLs (`//attacker.com/…`) also satisfy that check, so a crafted link such as `https://nocodb.example/#//attacker.com/phishing` silently redirected visitors to an attacker-controlled origin.

### Details

In `packages/nc-gui/plugins/hashRedirect.client.ts`, the plugin extracted the hash content and normalised it into `cleanUrl`:

```ts
let cleanUrl = hashPath.startsWith('/') ? hashPath : `/${hashPath}`
if (hashQuery) cleanUrl += `?${hashQuery}`
window.location.replace(cleanUrl)
```

`startsWith('/')` returns true for `//attacker.com/...`, which browsers interpret as a protocol-relative absolute URL. No hostname check was performed before the redirect. The fix adds an early `if (/^\/[/\\]/.test(hashPath)) return` to reject protocol-relative paths.

### Impact

- Open redirect from any NocoDB origin to an attacker-controlled domain.
- No authentication required; the attack lands the victim on an attacker-controlled page that may impersonate a NocoDB login.

### Credit

This issue was reported by [@fg0x0](https://github.com/fg0x0).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-rvp5-9p55-f5rp
- https://nvd.nist.gov/vuln/detail/CVE-2026-47377
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.04.1
