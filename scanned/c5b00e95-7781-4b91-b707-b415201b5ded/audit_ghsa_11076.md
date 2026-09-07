# [H] Gogs: DOM-based XSS via milestone selection

## Summary
Severity: High
Advisory: GHSA-vgjm-2cpf-4g7c
CVE: CVE-2026-26276
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-vgjm-2cpf-4g7c
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0

## Details
# Summary

It was confirmed in a test environment that an attacker can store an HTML/JavaScript payload in a repository’s **Milestone name**, and when another user selects that Milestone on the **New Issue** page (`/issues/new`), a **DOM-Based XSS** is triggered.

# Impact

* Theft of information accessible in the victim’s session.
* Extraction of CSRF tokens and submission of state-changing requests with the victim’s privileges.
* Repository operations performed with the victim’s privileges (Issue operations, settings changes, etc.).

(The impact scope depends on the victim’s permission level.)

# Remediation

A fix is available at https://github.com/gogs/gogs/releases/tag/v0.14.2

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-vgjm-2cpf-4g7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-26276
- https://github.com/gogs/gogs/pull/8178
- https://github.com/gogs/gogs/commit/9001a68cdda7bd9c078ffd6d1c4622905ac11e5c
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.2
