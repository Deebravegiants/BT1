# [M] CVE-2023-51385

## Summary
Severity: Medium
Advisory: CVE-2023-51385
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/CVE-2023-51385
Type: osv

## Details
In ssh in OpenSSH before 9.6, OS command injection might occur if a user name or host name has shell metacharacters, and this name is referenced by an expansion token in certain situations. For example, an untrusted Git repository can have a submodule with shell metacharacters in a user name or host name.

## References
- http://www.openwall.com/lists/oss-security/2025/10/07/1
- http://www.openwall.com/lists/oss-security/2025/10/12/1
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://cert-portal.siemens.com/productcert/html/ssa-794697.html
- https://support.apple.com/kb/HT214084
- https://vin01.github.io/piptagole/ssh/security/openssh/libssh/remote-code-execution/2023/12/20/openssh-proxycommand-libssh-rce.html
- https://www.openssh.com/txt/release-9.6
- https://www.openwall.com/lists/oss-security/2023/12/18/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51385.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-51385
- https://security.gentoo.org/glsa/202312-17
- https://security.netapp.com/advisory/ntap-20240105-0005/
- https://www.debian.org/security/2023/dsa-5586
- https://github.com/openssh/openssh-portable/commit/7ef3787c84b6b524501211b11a26c742f829af1a
- http://seclists.org/fulldisclosure/2024/Mar/21
- http://www.openwall.com/lists/oss-security/2023/12/26/4
- https://lists.debian.org/debian-lts-announce/2023/12/msg00017.html
