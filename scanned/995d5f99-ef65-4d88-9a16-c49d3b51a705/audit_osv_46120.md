# [M] JLSEC-2026-70

## Summary
Severity: Medium
Advisory: JLSEC-2026-70
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-70
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <9.9.1+0

## Details
In ssh in OpenSSH before 9.6, OS command injection might occur if a user name or host name has shell metacharacters, and this name is referenced by an expansion token in certain situations. For example, an untrusted Git repository can have a submodule with shell metacharacters in a user name or host name.

## References
- http://seclists.org/fulldisclosure/2024/Mar/21
- http://www.openwall.com/lists/oss-security/2023/12/26/4
- http://www.openwall.com/lists/oss-security/2025/10/07/1
- http://www.openwall.com/lists/oss-security/2025/10/12/1
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://cert-portal.siemens.com/productcert/html/ssa-794697.html
- https://github.com/openssh/openssh-portable/commit/7ef3787c84b6b524501211b11a26c742f829af1a
- https://lists.debian.org/debian-lts-announce/2023/12/msg00017.html
- https://security.gentoo.org/glsa/202312-17
- https://security.netapp.com/advisory/ntap-20240105-0005/
- https://support.apple.com/kb/HT214084
- https://vin01.github.io/piptagole/ssh/security/openssh/libssh/remote-code-execution/2023/12/20/openssh-proxycommand-libssh-rce.html
- https://www.debian.org/security/2023/dsa-5586
- https://www.openssh.com/txt/release-9.6
- https://www.openwall.com/lists/oss-security/2023/12/18/2
