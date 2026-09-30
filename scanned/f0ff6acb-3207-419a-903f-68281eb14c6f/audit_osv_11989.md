# [H] CVE-2018-1000546

## Summary
Severity: High
Advisory: CVE-2018-1000546
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000546
Type: osv

## Details
Triplea version <= 1.9.0.0.10291 contains a XML External Entity (XXE) vulnerability in Importing game data that can result in Possible information disclosure, server-side request forgery, or remote code execution. This attack appear to be exploitable via Specially crafted game data file (XML).

## References
- https://0dd.zone/2018/05/31/TripleA-XXE/
- https://github.com/triplea-game/triplea/issues/3442
