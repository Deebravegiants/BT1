# [H] CVE-2021-45394

## Summary
Severity: High
Advisory: CVE-2021-45394
Aliases: GHSA-6m93-343m-3jrc
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-18
Source: https://osv.dev/vulnerability/CVE-2021-45394
Type: osv

## Details
An issue was discovered in Spipu HTML2PDF before 5.2.4. Attackers can trigger deserialization of arbitrary data via the injection of a malicious <link> tag in the converted HTML document.

## References
- https://github.com/spipu/html2pdf/blob/master/CHANGELOG.md
- https://github.com/spipu/html2pdf
- https://www.synacktiv.com/sites/default/files/2022-01/html2pdf_ssrf_deserialization.pdf
