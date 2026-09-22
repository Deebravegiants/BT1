# [H] CVE-2022-45142

## Summary
Severity: High
Advisory: CVE-2022-45142
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2022-45142
Type: osv

## Details
The fix for CVE-2022-3437 included changing memcmp to be constant time and a workaround for a compiler bug by adding "!= 0" comparisons to the result of memcmp. When these patches were backported to the heimdal-7.7.1 and heimdal-7.8.0 branches (and possibly other branches) a logic inversion sneaked in causing the validation of message integrity codes in gssapi/arcfour to be inverted.

## References
- https://www.openwall.com/lists/oss-security/2023/02/08/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45142.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-45142
- https://security.gentoo.org/glsa/202310-06
