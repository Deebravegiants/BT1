# [H] NocoDB: Stored Cross-Site Scripting via Form View Redirect URL

## Summary
Severity: High
Advisory: GHSA-hj85-ph9q-78jg
CVE: CVE-2026-47387
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-hj85-ph9q-78jg
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary

The shared form-view submit handler in NocoDB writes the form's `redirect_url` to `window.location.href` after a same-host check that does not validate the URL scheme. A user with `editor` role (or above) on any base can plant a `javascript:` URL in the form's `redirect_url`; when an authenticated viewer opens the share-link and submits the form, the payload executes in the NocoDB origin and can read the session token from `localStorage["nocodb-gui-v2"]`.

### Details

The vulnerable sink is in `packages/nc-gui/composables/useSharedFormViewStore.ts`:

- `isValidRedirectUrl` validated only `typeof === 'string'` and non-empty trim — no scheme check.
- The submit branch built an anchor element, compared `anchor.host` to `window.location.host`, and either pushState-reloaded (same host) or assigned `window.location.href = redirectUrl` (otherwise).
- For non-network schemes such as `javascript:`, `data:`, `vbscript:`, and `file:`, `anchor.host` is the empty string, so the same-host check is false and the code falls into the external-redirect branch — executing the URL same-origin in the NocoDB tab.

The `redirect_url` field is writable by any user with `editor` role on the base via the form-view PATCH endpoint, and the value is returned verbatim by the public shared-view meta endpoint, so no further privilege is required to weaponize a public form share.

### Impact

- **Same-origin script execution in the viewer's NocoDB tab.** The payload runs in the NocoDB origin and can read the session token at `localStorage["nocodb-gui-v2"].token`.
- **Action under the viewer's identity.** With the token, an attacker can call authenticated APIs as the viewer, scoped to whatever workspaces, bases, and operations that viewer is permitted to use.
- **Single-click viewer flow.** Form share-links are the intended distribution channel for forms, so the phishing surface is on-brand; the form can be configured with a single hidden pre-filled required field to reduce the viewer flow to one click.

### Credit

This issue was reported by [@kah-ja](https://github.com/kah-ja) ([turingpoint.de](https://turingpoint.de)).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-hj85-ph9q-78jg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47387
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
