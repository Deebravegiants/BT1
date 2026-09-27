# [H] Glibc: buffer overflow in ld.so leading to privilege escalation

## Summary
Severity: High
Advisory: CVE-2023-4911
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-03
Source: https://osv.dev/vulnerability/CVE-2023-4911
Type: osv

## Details
A buffer overflow was discovered in the GNU C Library's dynamic loader ld.so while processing the GLIBC_TUNABLES environment variable. This issue could allow a local attacker to use maliciously crafted GLIBC_TUNABLES environment variables when launching binaries with SUID permission to execute code with elevated privileges.

## References
- http://packetstormsecurity.com/files/174986/glibc-ld.so-Local-Privilege-Escalation.html
- http://packetstormsecurity.com/files/176288/Glibc-Tunables-Privilege-Escalation.html
- http://seclists.org/fulldisclosure/2023/Oct/11
- http://www.openwall.com/lists/oss-security/2023/10/03/2
- http://www.openwall.com/lists/oss-security/2023/10/03/3
- http://www.openwall.com/lists/oss-security/2023/10/05/1
- http://www.openwall.com/lists/oss-security/2023/10/13/11
- http://www.openwall.com/lists/oss-security/2023/10/14/3
- http://www.openwall.com/lists/oss-security/2023/10/14/5
- http://www.openwall.com/lists/oss-security/2023/10/14/6
- https://access.redhat.com/downloads/content/package-browser/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-794697.html
- https://cert-portal.siemens.com/productcert/html/ssa-831302.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4DBUQRRPB47TC3NJOUIBVWUGFHBJAFDL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DFG4P76UHHZEWQ26FWBXG76N2QLKKPZA/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NDAQWHTSVOCOZ5K6KPIWKRT3JX4RTZUR/
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-4911
- https://www.exploit-db.com/exploits/52479
- https://www.qualys.com/2023/10/03/cve-2023-4911/looney-tunables-local-privilege-escalation-glibc-ld-so.txt
