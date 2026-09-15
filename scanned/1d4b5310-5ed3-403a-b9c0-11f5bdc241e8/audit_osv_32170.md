# [H] Remote Authentication-Bypass can lead to server crash or limited information disclosure due to faulty pattern matching

## Summary
Severity: High
Advisory: CVE-2025-25205
Aliases: CVE-2026-71209, GHSA-pg8v-5jcv-wrvw
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-25205
Type: osv

## Details
Audiobookshelf is a self-hosted audiobook and podcast server. Starting in version 2.17.0 and prior to version 2.19.1, a flaw in the authentication bypass logic allows unauthenticated requests to match certain unanchored regex patterns in the URL. Attackers can craft URLs containing substrings like "/api/items/1/cover" in a query parameter (?r=/api/items/1/cover) to partially bypass authentication or trigger server crashes under certain routes. This could lead to information disclosure of otherwise protected data and, in some cases, a complete denial of service (server crash) if downstream code expects an authenticated user object. Version 2.19.1 contains a patch for the issue.

## References
- https://github.com/advplyr/audiobookshelf/blob/1a3d70d04100924d41391acb55bd8ddca486a4fa/server/Auth.js#L17-L41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25205.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-pg8v-5jcv-wrvw
- https://nvd.nist.gov/vuln/detail/CVE-2025-25205
- https://github.com/advplyr/audiobookshelf/commit/bf8407274e3ee300af1927ee660d078a7a801e1c
- https://github.com/advplyr/audiobookshelf/commit/ec6537656925a43871b07cfee12c9f383844d224
- https://github.com/advplyr/audiobookshelf/pull/3584
