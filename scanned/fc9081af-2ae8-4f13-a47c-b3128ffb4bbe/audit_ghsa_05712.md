# [M] GI-DocGen vulnerable to Reflected XSS via unescaped query strings

## Summary
Severity: Medium
Advisory: GHSA-6p6h-rqr6-62mv
CVE: CVE-2025-11687
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-6p6h-rqr6-62mv
Type: github-advisory

## Affected
- PyPI: `gi-docgen` — affected >=0 <2025.5

## Details
A flaw was found in GI-DocGen. This vulnerability allows arbitrary JavaScript execution in the context of the page — enabling DOM access, session cookie theft and other client-side attacks — via a crafted URL that supplies a malicious value to the q GET parameter (reflected DOM XSS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11687
- https://access.redhat.com/security/cve/CVE-2025-11687
- https://bugzilla.redhat.com/show_bug.cgi?id=2403536
- https://github.com/GNOME/gi-docgen
- https://gitlab.gnome.org/GNOME/gi-docgen/-/commit/65d16b8ac178900602da540c8f5df4f52d5e8cf6
- https://gitlab.gnome.org/GNOME/gi-docgen/-/issues/228
