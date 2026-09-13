# [H] CVE-2020-25557

## Summary
Severity: High
Advisory: CVE-2020-25557
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-13
Source: https://osv.dev/vulnerability/CVE-2020-25557
Type: osv

## Details
In CMSuno 1.6.2, an attacker can inject malicious PHP code as a "username" while changing his/her username & password. After that, when attacker logs in to the application, attacker's code will be run. As a result of this vulnerability, authenticated user can run command on the server.

## References
- http://packetstormsecurity.com/files/161162/CMSUno-1.6.2-Remote-Code-Execution.html
- https://fatihhcelik.blogspot.com/2020/09/cmsuno-162-remote-code-execution.html
