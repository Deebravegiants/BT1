# [H] OAuth 2.1 Provider: Unprivileged users can register OAuth clients

## Summary
Severity: High
Advisory: GHSA-xr8f-h2gw-9xh6
CVE: CVE-2026-41427
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:L/SI:H/SA:N (CVSS_V4)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-xr8f-h2gw-9xh6
Type: github-advisory

## Affected
- npm: `@better-auth/oauth-provider` — affected >=1.4.8-beta.7 <1.6.5
- npm: `@better-auth/oauth-provider` — affected >=1.7.0-beta.0

## Details
### Am I affected?

  You're affected if all of the following are true:

  - Using @better-auth/oauth-provider at version specified below 
  - You configured clientPrivileges in the plugin options expecting it to gate who can create OAuth clients
  - The /oauth2/create-client or /admin/oauth2/create-client endpoints are reachable by authenticated users you don't fully trust

  If clientPrivileges is not configured, this bug has no security consequence for your deployment

  ---
  ### Summary

  The clientPrivileges option documents a create action, but the OAuth client creation endpoints did not invoke the hook before persisting new clients. Deployments that configured clientPrivileges to restrict client registration were not actually restricted — any authenticated user could reach the create endpoints and register an OAuth client with attacker-chosen redirect URIs and metadata.

 Non-create operations (read, list, update, delete, rotate) enforced the hook correctly. Only the create path was missing the check.

### Impact

  - Unauthorized registration of OAuth clients by any authenticated user, under deployments that expected clientPrivileges to block them.
  - Attacker-controlled redirect_uris on those clients enable phishing flows that present as registered first-party applications.
  - If the SERVER_ONLY admin creation endpoint is also exposed to low-privilege users (a separate deployment misconfiguration), additional sensitive fields including `skip_consent` become writable.

### Patches

Fixed in `@better-auth/oauth-provider@1.6.5` Both create endpoints now call the clientPrivileges hook with action "create" before persisting the client record.

### Workarounds

  If you cannot upgrade immediately:

  - Block the /oauth2/create-client and /admin/oauth2/create-client routes at your reverse proxy or middleware layer for any user who should not be able to register clients.
  - Do not expose the admin creation endpoint (it is SERVER_ONLY by design and should not be reachable by end-user sessions).

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-xr8f-h2gw-9xh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-41427
- https://github.com/better-auth/better-auth
