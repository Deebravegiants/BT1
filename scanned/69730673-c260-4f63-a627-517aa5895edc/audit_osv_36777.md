# [M] Zulip: Anonymous File Access After Disabling Spectator Access

## Summary
Severity: Medium
Advisory: CVE-2026-25742
Aliases: GHSA-f47p-xjqq-g28w
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-25742
Type: osv

## Details
Zulip is an open-source team collaboration tool. Prior to version 11.6, Zulip is an open-source team collaboration tool. From version 1.4.0 to before version 11.6, even after spectator access (enable_spectator_access / WEB_PUBLIC_STREAMS_ENABLED) is disabled, attachments originating from web-public streams can still be retrieved anonymously. As a result, file contents remain accessible even after public access is intended to be disabled. Similarly, even after spectator access is disabled, the /users/me/<stream_id>/topics endpoint remains reachable anonymously, allowing retrieval of topic history for web-public streams. This issue has been patched in version 11.6. This issue has been patched in version 11.6.

## References
- https://github.com/zulip/zulip/releases/tag/11.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25742.json
- https://github.com/zulip/zulip/security/advisories/GHSA-f47p-xjqq-g28w
- https://nvd.nist.gov/vuln/detail/CVE-2026-25742
- https://github.com/zulip/zulip/commit/3c045414299680b9f5dca7d76cf6cef6121c0236
- https://github.com/zulip/zulip/commit/41e23347b5218b3b0397a55176c7d97396735bae
