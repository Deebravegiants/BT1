# [H] CVE-2018-1000179

## Summary
Severity: High
Advisory: CVE-2018-1000179
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-08
Source: https://osv.dev/vulnerability/CVE-2018-1000179
Type: osv

## Details
A NULL Pointer Dereference of CWE-476 exists in quassel version 0.12.4 in the quasselcore void CoreAuthHandler::handle(const Login &msg) coreauthhandler.cpp line 235 that allows an attacker to cause a denial of service.

## References
- https://usn.ubuntu.com/4594-1/
- https://security.gentoo.org/glsa/201806-04
- https://www.debian.org/security/2018/dsa-4189
- https://github.com/quassel/quassel/blob/master/src/core/coreauthhandler.cpp#L236
