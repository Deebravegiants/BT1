# [C] CVE-2022-23852

## Summary
Severity: Critical
Advisory: CVE-2022-23852
Aliases: A-221255869, ASB-A-221255869
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-24
Source: https://osv.dev/vulnerability/CVE-2022-23852
Type: osv

## Details
Expat (aka libexpat) before 2.4.4 has a signed integer overflow in XML_GetBuffer, for configurations with a nonzero XML_CONTEXT_BYTES.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-484086.pdf
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.tenable.com/security/tns-2022-05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23852.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-23852
- https://security.gentoo.org/glsa/202209-24
- https://security.netapp.com/advisory/ntap-20220217-0001/
- https://www.debian.org/security/2022/dsa-5073
- https://github.com/libexpat/libexpat/pull/550
- https://lists.debian.org/debian-lts-announce/2022/03/msg00007.html
