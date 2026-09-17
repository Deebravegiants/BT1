# [H] DotPlant2 Improper Restriction of XML External Entity Reference

## Summary
Severity: High
Advisory: GHSA-c49v-35ff-q9f7
CVE: CVE-2020-25750
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c49v-35ff-q9f7
Type: github-advisory

## Affected
- Packagist: `devgroup/dotplant` — affected >=0 <2020-09-14

## Details
An issue was discovered in DotPlant2 before 2020-09-14. In class Pay2PayPayment in payment/Pay2PayPayment.php, there is an XXE vulnerability in the checkResult function. The user input ($_POST['xml']) is used for simplexml_load_string without sanitization. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25750
- https://github.com/DevGroup-ru/dotplant2/issues/400
- https://github.com/DevGroup-ru/dotplant2/commit/fee86c7052c227762c7325eb5c2811d9323f8429
