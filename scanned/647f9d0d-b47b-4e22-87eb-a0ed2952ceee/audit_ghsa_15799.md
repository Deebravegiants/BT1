# [M] Anki Latex Incomplete Blocklist Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x3r6-ccvq-cf5v
CVE: CVE-2024-29073
CWE: CWE-829
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-x3r6-ccvq-cf5v
Type: github-advisory

## Affected
- PyPI: `anki` — affected >=0 <24.6

## Details
An vulnerability in the handling of Latex exists in Ankitects Anki 24.04. When Latex is sanitized to prevent unsafe commands, the verbatim package, which comes installed by default in many Latex distributions, has been overlooked. A specially crafted flashcard can lead to an arbitrary file read. An attacker can share a flashcard to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29073
- https://github.com/ankitects/anki/pull/3218
- https://github.com/ankitects/anki/commit/06f7aa393d21d7d5dd8039e15d543b73c3346932
- https://github.com/ankitects/anki
- https://skerritt.blog/anki-0day
- https://skii.dev/anki-0day
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1992
