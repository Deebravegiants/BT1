# [C] CVE-2026-33587

## Summary
Severity: Critical
Advisory: CVE-2026-33587
Aliases: GHSA-f35w-wx37-26q7
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-33587
Type: osv

## Details
Lack of user input sanitisation in Open Notebook v1.8.3 allows the application user to execute Python code (and subsequently OS commands) on the docker container via Server-Side Template Injection (SSTI) for user-created transformations.

## References
- https://github.com/lfnovo/open-notebook/security/advisories/GHSA-f35w-wx37-26q7
