# [M] CVE-2019-11519

## Summary
Severity: Medium
Advisory: CVE-2019-11519
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-25
Source: https://osv.dev/vulnerability/CVE-2019-11519
Type: osv

## Details
Libraries/Nop.Services/Localization/LocalizationService.cs in nopCommerce through 4.10 allows XXE via the "Configurations -> Languages -> Edit Language -> Import Resources -> Upload XML file" screen.

## References
- https://www.nopcommerce.com/boards/t/62390/xxe-version-390.aspx
- https://github.com/nopSolutions/nopCommerce/issues/3713
