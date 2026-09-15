# [H] CVE-2020-5209

## Summary
Severity: High
Advisory: CVE-2020-5209
Aliases: GHSA-fw72-r8xm-45p8
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2020-5209
Type: osv

## Details
In NetHack before 3.6.5, unknown options starting with -de and -i can cause a buffer overflow resulting in a crash or remote code execution/privilege escalation. This vulnerability affects systems that have NetHack installed suid/sgid and shared systems that allow users to influence command line options. Users should upgrade to NetHack 3.6.5.

## References
- https://github.com/NetHack/NetHack/security/advisories/GHSA-fw72-r8xm-45p8
- https://github.com/NetHack/NetHack/commit/f3def5c0b999478da2d0a8f0b6a7c370a2065f77
