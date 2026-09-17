# [M] This flaw allows a malicious HTTP server to set "super cookies" in curl that are then passed back to...

## Summary
Severity: Medium
Advisory: JLSEC-2026-411
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-411
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.5.0+0

## Details
This flaw allows a malicious HTTP server to set "super cookies" in curl that
are then passed back to more origins than what is otherwise allowed or
possible. This allows a site to set cookies that then would get sent to
different and unrelated sites and domains.

It could do this by exploiting a mixed case flaw in curl's function that
verifies a given cookie domain against the Public Suffix List (PSL). For
example a cookie could be set with `domain=co.UK` when the URL used a lower
case hostname `curl.co.uk`, even though `co.uk` is listed as a PSL domain.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-093430.html
- https://cert-portal.siemens.com/productcert/html/ssa-202008.html
- https://cert-portal.siemens.com/productcert/html/ssa-331112.html
- https://curl.se/docs/CVE-2023-46218.html
- https://github.com/advisories/GHSA-59mm-6rr4-j9p2
- https://hackerone.com/reports/2212193
- https://lists.debian.org/debian-lts-announce/2023/12/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3ZX3VW67N4ACRAPMV2QS2LVYGD7H2MVE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3ZX3VW67N4ACRAPMV2QS2LVYGD7H2MVE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UOGXU25FMMT2X6UUITQ7EZZYMJ42YWWD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UOGXU25FMMT2X6UUITQ7EZZYMJ42YWWD/
- https://nvd.nist.gov/vuln/detail/CVE-2023-46218
- https://security.netapp.com/advisory/ntap-20240125-0007
- https://security.netapp.com/advisory/ntap-20240125-0007/
- https://www.debian.org/security/2023/dsa-5587
