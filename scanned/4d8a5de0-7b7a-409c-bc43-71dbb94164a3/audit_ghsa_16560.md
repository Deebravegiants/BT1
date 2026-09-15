# [H] gregwar/rst Local File Inclusion Vulnerability

## Summary
Severity: High
Advisory: GHSA-2gq2-m628-33xp
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-2gq2-m628-33xp
Type: github-advisory

## Affected
- Packagist: `gregwar/rst` — affected >=0 <1.0.3

## Details
A Local File Inclusion (LFI) vulnerability has been discovered in the gregwar/rst library, potentially exposing sensitive files on the server to unauthorized users. The issue arises from inadequate input validation, allowing an attacker to manipulate file paths and include arbitrary files.

## References
- https://github.com/Gregwar/RST/pull/34
- https://github.com/Gregwar/RST/commit/e8d90ccbeddd91ba3abc506079661dce234f9870
- https://hackerone.com/reports/179034
- https://github.com/FriendsOfPHP/security-advisories/blob/master/gregwar/rst/2016-10-31.yaml
- https://github.com/Gregwar/RST
