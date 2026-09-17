# [C] CVE-2025-12642

## Summary
Severity: Critical
Advisory: CVE-2025-12642
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-11-03
Source: https://osv.dev/vulnerability/CVE-2025-12642
Type: osv

## Details
lighttpd1.4.80 incorrectly merged trailer fields into headers after http request parsing. This behavior can be exploited to conduct HTTP Header Smuggling attacks.

Successful exploitation may allow an attacker to:

  *  Bypass access control rules
  *  Inject unsafe input into backend logic that trusts request headers
  *  Execute HTTP Request Smuggling attacks under some conditions


This issue affects lighttpd1.4.80

## References
- https://github.com/lighttpd/lighttpd1.4/commit/35cb89c103877de62d6b63d0804255475d77e5e1
