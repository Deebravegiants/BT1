# [C] Capgo API Key Manager Authentication Bypass via x-limited-key-id

## Summary
Severity: Critical
Advisory: CVE-2026-88862
Aliases: GHSA-5hjr-xhx8-x5j7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88862
Type: osv

## Details
Capgo (capgo.app) backend through 12.242.4 does not validate parent-child delegation when processing the x-limited-key-id header. checkKeyByIdPg() in supabase/functions/_backend/utils/hono_middleware.ts resolves the attacker-supplied numeric API key ID using only the key ID, its expiration state, and the authenticating key's user_id, while hasLimitedRbacSubkeyScope() accepts any key with a non-organization (e.g., app-scoped) RBAC binding and validateSubkeyUser() only compares owning user IDs. Because Capgo treats API keys as independent RBAC principals with separate role bindings, an authenticated apikey_manager API key with no application access can supply the numeric ID of a more privileged same-owner key and have the middleware replace the authenticated principal and effective API-key secret with that key (setSubkeyAuthContext), exercising an app_admin sibling's permissions without knowing or submitting its secret. The issue was reproduced on release 12.242.4 (commit b3d02cdbc23ac59990785acacd1f113c07458568) after the fix for GHSA-8h52-44r7-w343; at the time of the advisory no patched version was available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88862.json
- https://github.com/Cap-go/capgo.app/security/advisories/GHSA-5hjr-xhx8-x5j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-88862
- https://www.vulncheck.com/advisories/capgo-api-key-manager-authentication-bypass-via-x-limited-key-id
