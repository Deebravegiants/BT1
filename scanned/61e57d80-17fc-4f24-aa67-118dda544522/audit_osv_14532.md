# [H] CVE-2019-1010127

## Summary
Severity: High
Advisory: CVE-2019-1010127
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-1010127
Type: osv

## Details
VCFTools vcftools prior to version 0.1.15 is affected by: Use-after-free. The impact is: Denial of Service or possibly other impact (eg. code execution or information disclosure). The component is: The header::add_FILTER_descriptor method in header.cpp. The attack vector is: The victim must open a specially crafted VCF file.

## References
- https://github.com/vcftools/vcftools/issues/141
- https://docs.google.com/document/d/e/2PACX-1vQJveVcGMp_NMdBY5Je2K2k63RoCYznvKjJk5u1wJRmLotvwQkG5qiqZjpABcOkjzj49wkwGweiFwrc/pub
