# [C] Improper Restriction of XML External Entity Reference in dompdf/dompdf

## Summary
Severity: Critical
Advisory: GHSA-3vjh-xrhf-v9xh
CVE: CVE-2021-3902
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-3vjh-xrhf-v9xh
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <2.0.0

## Details
An improper restriction of external entities (XXE) vulnerability in dompdf/dompdf's SVG parser allows for Server-Side Request Forgery (SSRF) and deserialization attacks. This issue affects all versions prior to 2.0.0. The vulnerability can be exploited even if the isRemoteEnabled option is set to false. It allows attackers to perform SSRF, disclose internal image files, and cause PHAR deserialization attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3902
- https://github.com/dompdf/dompdf/commit/f56bc8e40be6c0ae0825e6c7396f4db80620b799
- https://github.com/dompdf/dompdf
- https://huntr.com/bounties/a6071c07-806f-429a-8656-a4742e4191b1
