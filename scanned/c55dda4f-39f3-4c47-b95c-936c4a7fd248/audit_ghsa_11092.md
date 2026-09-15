# [M] Gogs: Stored XSS in branch and wiki views through author and committer names

## Summary
Severity: Medium
Advisory: GHSA-vgvf-m4fw-938j
CVE: CVE-2026-26195
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-vgvf-m4fw-938j
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0

## Details
### Summary

Stored XSS is still possible through unsafe template rendering that mixes user input with `safe()` plus permissive sanitizer handling of data URLs.

### Details

`safe()` still turns off escaping:
- internal/template/template.go
- `func safe(raw string) template.HTML { return template.HTML(raw) }`

Branch pages still render committer names using `safe()`:
- templates/repo/branches/overview.tmpl
- templates/repo/branches/all.tmpl
- templates/repo/wiki/view.tmpl

The locale still injects a raw second argument: conf/locale/locale_en-US.ini (`branches.updated_by = updated %[1]s by %[2]s`)

### Impact

An attacker who can inject commit metadata such as author/committer name can trigger script execution on affected pages, leading to session abuse, CSRF token theft, or unauthorized actions.

### Recommended Fix

- Untrusted arguments should be escaped before being used in translations.
- Data URLs should be limited or blocked in the sanitizer.

### Remediation
A fix is available at https://github.com/gogs/gogs/releases/tag/v0.14.2.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-vgvf-m4fw-938j
- https://nvd.nist.gov/vuln/detail/CVE-2026-26195
- https://github.com/gogs/gogs/pull/8176
- https://github.com/gogs/gogs/commit/ac21150a53bef3a3061f4da787ab193a8d68ecfc
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.2
