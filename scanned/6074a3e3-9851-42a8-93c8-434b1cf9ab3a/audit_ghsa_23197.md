# [M] SOAPpy vulnerable to XXE attacks

## Summary
Severity: Medium
Advisory: GHSA-2gh8-gr6x-7q26
CVE: CVE-2014-3243
CWE: CWE-119
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2gh8-gr6x-7q26
Type: github-advisory

## Affected
- PyPI: `SOAPpy` — affected >=0 <0.12.6

## Details
SOAPpy 0.12.5 does not properly detect recursion during entity expansion, which allows remote attackers to cause a denial of service (memory and CPU consumption) via a crafted SOAP request containing a large number of nested entity references.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3243
- https://github.com/kiorky/SOAPpy/commit/64125a24aad228761f38312d44bde4bec7354276
- https://github.com/kiorky/SOAPpy/commit/a38656817c8ce7d02e117b1308328419a5d1560f
- https://github.com/kiorky/SOAPpy/blob/develop/CHANGES.txt#L32-L37
- https://web.archive.org/web/20150501220613/http://www.pnigos.com/?p=260
- https://web.archive.org/web/20200229062311/http://www.securityfocus.com/bid/67216
- http://seclists.org/fulldisclosure/2014/May/20
- http://www.openwall.com/lists/oss-security/2014/05/06/1
- http://www.openwall.com/lists/oss-security/2014/05/06/9
