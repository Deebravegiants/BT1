# [H] Notepad++ vulnerable to heap buffer write overflow in Utf8_16_Read::convert

## Summary
Severity: High
Advisory: CVE-2023-40031
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-25
Source: https://osv.dev/vulnerability/CVE-2023-40031
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Versions 8.5.6 and prior are vulnerable to heap buffer write overflow in `Utf8_16_Read::convert`. This issue may lead to arbitrary code execution. As of time of publication, no known patches are available in existing versions of Notepad++.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40031.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40031
- https://securitylab.github.com/advisories/GHSL-2023-092_Notepad__/
