# [H] CVE-2020-14939

## Summary
Severity: High
Advisory: CVE-2020-14939
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-06-23
Source: https://osv.dev/vulnerability/CVE-2020-14939
Type: osv

## Details
An issue was discovered in savestruct_internal.c in FreedroidRPG 1.0rc2. Saved game files are composed of Lua scripts that recover a game's state. A file can be modified to put any Lua code inside, leading to arbitrary code execution while loading.

## References
- https://bugs.freedroid.org/b/issue953
- https://logicaltrust.net/blog/2020/02/freedroid.html
