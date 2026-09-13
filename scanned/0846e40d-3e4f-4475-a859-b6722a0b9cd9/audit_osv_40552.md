# [M] oasdiff actions resolve external $refs by default, enabling SSRF and disclosure of structured files on pull-request runs

## Summary
Severity: Medium
Advisory: CVE-2026-53507
Aliases: GHSA-fhj3-7267-7vv5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-53507
Type: osv

## Details
oasdiff-action is a GitHub Action that detects breaking changes in OpenAPI specs and post a review on every pull request. Before version 0.0.51, the oasdiff actions resolved external $refs in the OpenAPI spec by default (allow-external-refs: true). When an action runs on a pull request whose spec is attacker-controlled — most importantly fork pull requests on public repositories — a $ref in that spec is fetched/read on the runner with no interaction required, enabling SSRF and disclosure of structured files on the runner. This issue has been patched in version 0.0.51.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53507.json
- https://github.com/oasdiff/oasdiff-action/security/advisories/GHSA-fhj3-7267-7vv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53507
- https://github.com/oasdiff/oasdiff-action/pull/128
- https://github.com/oasdiff/oasdiff-action/pull/129
- https://github.com/oasdiff/oasdiff-action/pull/130
