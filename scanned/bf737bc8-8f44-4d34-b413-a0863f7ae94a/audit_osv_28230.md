# [H] CVE-2024-2961

## Summary
Severity: High
Advisory: CVE-2024-2961
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-2961
Type: osv

## Details
The iconv() function in the GNU C Library versions 2.39 and older may overflow the output buffer passed to it by up to 4 bytes when converting strings to the ISO-2022-CN-EXT character set, which may be used to crash an application or overwrite a neighbouring variable.

## References
- http://www.openwall.com/lists/oss-security/2024/04/17/9
- http://www.openwall.com/lists/oss-security/2024/04/18/4
- http://www.openwall.com/lists/oss-security/2024/04/24/2
- http://www.openwall.com/lists/oss-security/2024/05/27/1
- http://www.openwall.com/lists/oss-security/2024/05/27/2
- http://www.openwall.com/lists/oss-security/2024/05/27/3
- http://www.openwall.com/lists/oss-security/2024/05/27/4
- http://www.openwall.com/lists/oss-security/2024/05/27/5
- http://www.openwall.com/lists/oss-security/2024/05/27/6
- http://www.openwall.com/lists/oss-security/2024/07/22/5
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.debian.org/debian-lts-announce/2024/05/msg00001.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BTJFBGHDYG5PEIFD5WSSSKSFZ2AZWC5N/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/P3I4KYS6EU6S7QZ47WFNTPVAHFIUQNEL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YAMJQI3Y6BHWV3CUTYBXOZONCUJNOB2Z/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2961.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2961
- https://security.netapp.com/advisory/ntap-20240531-0002/
- https://sourceware.org/git/?p=glibc.git;a=blob;f=advisories/GLIBC-SA-2024-0004
- https://www.ambionics.io/blog/iconv-cve-2024-2961-p1
