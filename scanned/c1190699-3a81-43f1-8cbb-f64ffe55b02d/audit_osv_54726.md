# [C] CVE-2024-30949

## Summary
Severity: Critical
Advisory: CVE-2024-30949
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-20
Source: https://osv.dev/vulnerability/CVE-2024-30949
Type: osv

## Details
An issue in newlib v.4.3.0 allows an attacker to execute arbitrary code via the time unit scaling in the _gettimeofday function.

## References
- https://sourceware.org/git/?p=newlib-cygwin.git%3Ba=commit%3Bh=5f15d7c5817b07a6b18cbab17342c95cb7b42be4
- https://gist.github.com/visitorckw/6b26e599241ea80210ea136b28441661
- https://inbox.sourceware.org/newlib/20231129035714.469943-1-visitorckw%40gmail.com/
