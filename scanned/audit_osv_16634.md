# [C] CVE-2019-8341

## Summary
Severity: Critical
Advisory: CVE-2019-8341
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-15
Source: https://osv.dev/vulnerability/CVE-2019-8341
Type: osv

## Details
An issue was discovered in Jinja2 2.10. The from_string function is prone to Server Side Template Injection (SSTI) where it takes the "source" parameter as a template object, renders it, and then returns it. The attacker can exploit it with {{INJECTION COMMANDS}} in a URI. NOTE: The maintainer and multiple third parties believe that this vulnerability isn't valid because users shouldn't use untrusted templates without sandboxing

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00064.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1677653
- https://bugzilla.suse.com/show_bug.cgi?id=1125815
- https://github.com/JameelNabbo/Jinja2-Code-execution
- https://www.exploit-db.com/exploits/46386/
