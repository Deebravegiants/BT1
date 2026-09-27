# [H] CVE-2022-42898

## Summary
Severity: High
Advisory: CVE-2022-42898
Aliases: GHSA-64mq-fvfj-5x3c
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/CVE-2022-42898
Type: osv

## Details
PAC parsing in MIT Kerberos 5 (aka krb5) before 1.19.4 and 1.20.x before 1.20.1 has integer overflows that may lead to remote code execution (in KDC, kadmind, or a GSS or Kerberos application server) on 32-bit platforms (which have a resultant heap-based buffer overflow), and cause a denial of service on other platforms. This occurs in krb5_pac_parse in lib/krb5/krb/pac.c. Heimdal before 7.7.1 has "a similar bug."

## References
- https://web.mit.edu/kerberos/krb5-1.19/
- https://web.mit.edu/kerberos/krb5-1.20/README-1.20.1.txt
- https://www.samba.org/samba/security/CVE-2022-42898.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42898.json
- https://github.com/heimdal/heimdal/security/advisories/GHSA-64mq-fvfj-5x3c
- https://nvd.nist.gov/vuln/detail/CVE-2022-42898
- https://security.gentoo.org/glsa/202309-06
- https://security.gentoo.org/glsa/202310-06
- https://security.netapp.com/advisory/ntap-20230216-0008/
- https://security.netapp.com/advisory/ntap-20230223-0001/
- https://web.mit.edu/kerberos/advisories/
- https://bugzilla.samba.org/show_bug.cgi?id=15203
- https://github.com/krb5/krb5/commit/ea92d2f0fcceb54a70910fa32e9a0d7a5afc3583
