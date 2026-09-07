# [M] Spipu HTML2PDF vulnerable to cross-site scripting 

## Summary
Severity: Medium
Advisory: GHSA-99fg-2h75-m92h
CVE: CVE-2023-39062
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-28
Source: https://github.com/advisories/GHSA-99fg-2h75-m92h
Type: github-advisory

## Affected
- Packagist: `spipu/html2pdf` — affected >=0 <5.2.8

## Details
Cross Site Scripting vulnerability in Spipu HTML2PDF before v.5.2.8 allows a remote attacker to execute arbitrary code via a crafted script to the forms.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39062
- https://github.com/spipu/html2pdf/commit/92afd81823d62ad95eb9d034858311bb63aeb4ac
- https://github.com/afine-com/CVE-2023-39062
- https://github.com/sectroyer/CVEs/tree/main/CVE-2023-39062
- https://github.com/spipu/html2pdf
- https://github.com/spipu/html2pdf/blob/92afd81823d62ad95eb9d034858311bb63aeb4ac/CHANGELOG.md
