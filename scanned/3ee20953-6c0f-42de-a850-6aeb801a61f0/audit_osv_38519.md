# [H] iconv crash due to assertion failure with untrusted input

## Summary
Severity: High
Advisory: CVE-2026-4046
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-4046
Type: osv

## Details
The iconv() function in the GNU C Library versions 2.43 and earlier may crash due to an assertion failure when converting inputs from the IBM1390 or IBM1399 character sets, which may be used to remotely crash an application.



This vulnerability can be trivially mitigated by removing the IBM1390 and IBM1399 character sets from systems that do not need them.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4046.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4046
- https://sourceware.org/git/?p=glibc.git;a=blob_plain;f=advisories/GLIBC-SA-2026-0007;hb=HEAD
- https://sourceware.org/bugzilla/show_bug.cgi?id=33980
- https://inbox.sourceware.org/libc-announce/76814edf-cf7f-47ec-979d-2dce0a2c76bf@gotplt.org/T/#u
