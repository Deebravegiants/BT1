# [H] Ankitects Anki arbitrary script execution vulnerability

## Summary
Severity: High
Advisory: GHSA-9gq7-p5w9-w899
CVE: CVE-2024-26020
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-9gq7-p5w9-w899
Type: github-advisory

## Affected
- PyPI: `anki` — affected >=0 <24.06

## Details
An arbitrary script execution vulnerability exists in the MPV functionality of Ankitects Anki 24.04. A specially crafted flashcard can lead to a arbitrary code execution. An attacker can send malicious flashcard to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26020
- https://github.com/ankitects/anki/commit/8d2e8b1e4fa3757581f224b1a57057d0455352ce
- https://github.com/ankitects/anki
- https://skerritt.blog/anki-0day
- https://skii.dev/anki-0day
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1993
