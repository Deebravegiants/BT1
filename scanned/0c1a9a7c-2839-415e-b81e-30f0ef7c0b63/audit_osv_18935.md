# [C] CVE-2020-5214

## Summary
Severity: Critical
Advisory: CVE-2020-5214
Aliases: GHSA-p8fw-rq89-xqx6
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2020-5214
Type: osv

## Details
In NetHack before 3.6.5, detecting an unknown configuration file option can cause a buffer overflow resulting in a crash or remote code execution/privilege escalation. This vulnerability affects systems that have NetHack installed suid/sgid and shared systems that allow users to upload their own configuration files. Users should upgrade to NetHack 3.6.5.

## References
- https://github.com/NetHack/NetHack/security/advisories/GHSA-p8fw-rq89-xqx6
