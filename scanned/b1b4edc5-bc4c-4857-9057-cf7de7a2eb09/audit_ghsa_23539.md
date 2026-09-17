# [H] mPDF Unsafe Deserialization

## Summary
Severity: High
Advisory: GHSA-3cwc-m7c2-qr86
CVE: CVE-2019-1000005
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3cwc-m7c2-qr86
Type: github-advisory

## Affected
- Packagist: `mpdf/mpdf` — affected >=0 <7.1.8

## Details
mPDF version 7.1.7 and earlier contains a CWE-502: Deserialization of Untrusted Data vulnerability in getImage() method of Image/ImageProcessor class that can result in Arbitry code execution, file write, etc.. This attack appears to be exploitable via attacker must host crafted image on victim server and trigger generation of pdf file with content `<img src="phar://path/to/crafted/image">`. This vulnerability appears to have been fixed in 7.1.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1000005
- https://github.com/mpdf/mpdf/issues/949
- https://github.com/mpdf/mpdf
