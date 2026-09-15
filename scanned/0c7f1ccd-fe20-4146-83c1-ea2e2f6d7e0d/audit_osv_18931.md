# [H] CVE-2020-5210

## Summary
Severity: High
Advisory: CVE-2020-5210
Aliases: GHSA-v5pg-hpjg-9rpp
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2020-5210
Type: osv

## Details
In NetHack before 3.6.5, an invalid argument to the -w command line option can cause a buffer overflow resulting in a crash or remote code execution/privilege escalation. This vulnerability affects systems that have NetHack installed suid/sgid and shared systems that allow users to influence command line options. Users should upgrade to NetHack 3.6.5.

## References
- https://github.com/NetHack/NetHack/security/advisories/GHSA-v5pg-hpjg-9rpp
- https://github.com/NetHack/NetHack/commit/f3def5c0b999478da2d0a8f0b6a7c370a2065f77
