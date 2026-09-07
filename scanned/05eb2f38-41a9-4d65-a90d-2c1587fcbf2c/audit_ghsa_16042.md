# [H] Cross Site Scripting vulnerability in Snipe-IT

## Summary
Severity: High
Advisory: GHSA-hw9x-8m75-4vjq
CVE: CVE-2024-51093
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-hw9x-8m75-4vjq
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0

## Details
Cross Site Scripting vulnerability in Snipe-IT v.7.0.13 allows a remote attacker to escalate privileges via an unknown part of the file /users/{{user-id}}/#files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-51093
- https://gist.githubusercontent.com/Tommywarren/ca70f1c43f4ec34dc19cd13459535780/raw/d13192ae50bc7c024b922412dfa3f530faa8d5db/CVE-2024-51093
- https://github.com/snipe/snipe-it
