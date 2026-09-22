# [M] LobeChat 2.2.9 - Broken Object-Level Authorization in Message Sub-Resource Writes

## Summary
Severity: Medium
Advisory: CVE-2026-58580
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-58580
Type: osv

## Details
LobeChat through 2.2.9 server-database deployments are vulnerable to broken object-level authorization in MessageModel. The updateMessagePlugin, updatePluginState, updatePluginError, updateTTS and updateTranslate methods filter target rows by message id alone, omitting the userId scope that sibling methods apply, and findMessagePlugin reads back by id alone. Reachable via the corresponding tRPC message procedures, an authenticated user who knows another user's message identifier can overwrite that victim's plugin tool-call metadata, plugin state/error, text-to-speech and translation records on the same instance, and the tampered content is served back to the victim. Exploitation requires knowledge of the victim's non-enumerable message identifier.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58580.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58580
- https://www.vulncheck.com/advisories/lobechat-broken-object-level-authorization-in-message-sub-resource-writes
- https://github.com/lobehub/lobehub/issues/16534
- https://github.com/lobehub/lobehub
