# [M] CVE-2023-51384

## Summary
Severity: Medium
Advisory: CVE-2023-51384
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/CVE-2023-51384
Type: osv

## Details
In ssh-agent in OpenSSH before 9.6, certain destination constraints can be incompletely applied. When destination constraints are specified during addition of PKCS#11-hosted private keys, these constraints are only applied to the first key, even if a PKCS#11 token returns multiple keys.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://cert-portal.siemens.com/productcert/html/ssa-794697.html
- https://support.apple.com/kb/HT214084
- https://www.openssh.com/txt/release-9.6
- https://www.openwall.com/lists/oss-security/2023/12/18/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51384.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-51384
- https://security.netapp.com/advisory/ntap-20240105-0005/
- https://www.debian.org/security/2023/dsa-5586
- https://github.com/openssh/openssh-portable/commit/881d9c6af9da4257c69c327c4e2f1508b2fa754b
- http://seclists.org/fulldisclosure/2024/Mar/21
