# [C] Magento php object injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-337c-3rch-q35j
CVE: CVE-2020-9664
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-337c-3rch-q35j
Type: github-advisory

## Affected
- Packagist: `magento/core` — affected >=0

## Details
Magento versions 1.14.4.5 and earlier, and 1.9.4.5 and earlier have a php object injection vulnerability. Successful exploitation could lead to arbitrary code execution.
A patch SUPEE-11346 is available at [Magento Open Source Download Page](https://github.com/m-a-org/magento-patches) > Release Archive Tab > Magento Open Source Patches - 1.x Section

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9664
- https://helpx.adobe.com/security/products/magento/apsb20-41.html
