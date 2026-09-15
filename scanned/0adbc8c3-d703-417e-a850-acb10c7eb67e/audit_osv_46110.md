# [M] JLSEC-2026-69

## Summary
Severity: Medium
Advisory: JLSEC-2026-69
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-69
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=8.9.0+0 <9.9.1+0

## Details
In ssh-agent in OpenSSH before 9.6, certain destination constraints can be incompletely applied. When destination constraints are specified during addition of PKCS#11-hosted private keys, these constraints are only applied to the first key, even if a PKCS#11 token returns multiple keys.

## References
- http://seclists.org/fulldisclosure/2024/Mar/21
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://cert-portal.siemens.com/productcert/html/ssa-794697.html
- https://github.com/openssh/openssh-portable/commit/881d9c6af9da4257c69c327c4e2f1508b2fa754b
- https://security.netapp.com/advisory/ntap-20240105-0005/
- https://support.apple.com/kb/HT214084
- https://www.debian.org/security/2023/dsa-5586
- https://www.openssh.com/txt/release-9.6
- https://www.openwall.com/lists/oss-security/2023/12/18/2
