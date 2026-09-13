# [H] CVE-2020-25623

## Summary
Severity: High
Advisory: CVE-2020-25623
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-02
Source: https://osv.dev/vulnerability/CVE-2020-25623
Type: osv

## Details
Erlang/OTP 22.3.x before 22.3.4.6 and 23.x before 23.1 allows Directory Traversal. An attacker can send a crafted HTTP request to read arbitrary files, if httpd in the inets application is used.

## References
- https://github.com/erlang/otp/releases/tag/OTP-23.1
- https://www.erlang.org/downloads
- https://www.erlang.org/news
