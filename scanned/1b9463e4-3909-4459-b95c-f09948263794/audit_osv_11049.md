# [M] CVE-2017-5852

## Summary
Severity: Medium
Advisory: CVE-2017-5852
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5852
Type: osv

## Details
The PoDoFo::PdfPage::GetInheritedKeyFromObject function in base/PdfVariant.cpp in PoDoFo 0.9.4 allows remote attackers to cause a denial of service (infinite loop) via a crafted file.

## References
- http://www.securityfocus.com/bid/97032
- http://www.openwall.com/lists/oss-security/2017/02/01/12
- http://www.openwall.com/lists/oss-security/2017/02/02/10
- https://blogs.gentoo.org/ago/2017/02/01/podofo-infinite-loop-in-podofopdfpagegetinheritedkeyfromobject-pdfpage-cpp/
