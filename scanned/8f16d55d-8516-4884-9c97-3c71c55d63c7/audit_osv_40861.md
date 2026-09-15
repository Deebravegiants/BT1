# [H] OpenReplay: Cross-user IDOR in notes and dashboard widgets

## Summary
Severity: High
Advisory: CVE-2026-55880
Aliases: GHSA-9xfv-p2fx-vmx9
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55880
Type: osv

## Details
OpenReplay is a self-hosted session replay suite. In 1.27.0 and earlier, three dashboard and note mutation functions ran their SQL without the ownership predicate that their sibling read and edit functions use: notes.delete filtered only on note id and project id, while dashboards.update_widget and dashboards.remove_widget filtered only on dashboard id and widget id, allowing any authenticated member to delete another user's private session notes and remove or rewrite widgets on another user's private dashboards.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55880.json
- https://github.com/openreplay/openreplay/security/advisories/GHSA-9xfv-p2fx-vmx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-55880
