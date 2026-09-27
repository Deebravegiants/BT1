# [H] CVE-2024-45491

## Summary
Severity: High
Advisory: CVE-2024-45491
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-08-30
Source: https://osv.dev/vulnerability/CVE-2024-45491
Type: osv

## Details
An issue was discovered in libexpat before 2.6.3. dtdCopy in xmlparse.c can have an integer overflow for nDefaultAtts on 32-bit platforms (where UINT_MAX equals SIZE_MAX).

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00036.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45491.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45491
- https://security.netapp.com/advisory/ntap-20241018-0003/
- https://github.com/libexpat/libexpat/issues/888
- https://github.com/libexpat/libexpat/pull/891
