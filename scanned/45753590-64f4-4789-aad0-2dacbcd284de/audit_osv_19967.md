# [H] CVE-2021-28667

## Summary
Severity: High
Advisory: CVE-2021-28667
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-18
Source: https://osv.dev/vulnerability/CVE-2021-28667
Type: osv

## Details
StackStorm before 3.4.1, in some situations, has an infinite loop that consumes all available memory and disk space. This can occur if Python 3.x is used, the locale is not utf-8, and there is an attempt to log Unicode data (from an action or rule name).

## References
- https://stackstorm.com/2021/03/10/stackstorm-v3-4-1-security-fix/
