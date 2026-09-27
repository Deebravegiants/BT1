# [C] Vikunja 0.24.0 Broken Object Level Authorization via Link-Share Token

## Summary
Severity: Critical
Advisory: CVE-2026-68582
Aliases: GHSA-rj9j-8772-4h6c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-02
Source: https://osv.dev/vulnerability/CVE-2026-68582
Type: osv

## Details
Vikunja versions >= 0.24.0 and <= 2.3.0 contain a broken object level authorization (BOLA) vulnerability in the task-collection endpoint (GET /api/v1/projects/{project}/views/{view}/tasks). The endpoint loads the requested project view from the URL path without verifying the caller is authorized for it. For a link-share token holder, the task scope is pinned to the share's own project, but the view is taken from the attacker-controlled path and never re-validated. As a result, a holder of any project share link can read any other tenant's kanban bucket records — bucket titles and the full created_by user object (username, name, id) — for every view in the instance. The same missing pre-authorization view load also creates a project/view-ID existence oracle (404 vs. non-404) usable by link shares and ordinary authenticated users. Task contents remain constrained to the share's own project and are not disclosed. Fixed in 2.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68582.json
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-rj9j-8772-4h6c
- https://nvd.nist.gov/vuln/detail/CVE-2026-68582
- https://www.vulncheck.com/advisories/vikunja-broken-object-level-authorization-via-link-share-token
