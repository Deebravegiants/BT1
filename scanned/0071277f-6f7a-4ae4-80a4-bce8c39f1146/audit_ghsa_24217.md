# [H] Shopware Insecure Deserialization Vulnerability

## Summary
Severity: High
Advisory: GHSA-rf8f-hqjv-986p
CVE: CVE-2019-12799
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rf8f-hqjv-986p
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.3.0

## Details
In createInstanceFromNamedArguments in Shopware through 5.6.x, a crafted web request can trigger a PHP object instantiation vulnerability, which can result in an arbitrary deserialization if the right class is instantiated. An attacker can leverage this deserialization to achieve remote code execution. NOTE: this issue is a bypass for a CVE-2017-18357 whitelist patch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12799
- https://github.com/rapid7/metasploit-framework/pull/11828
- https://github.com/advisories/GHSA-6m27-7cqj-2mxw
- https://github.com/shopware5/shopware
- https://web.archive.org/web/20171112153855/https://blog.ripstech.com/2017/shopware-php-object-instantiation-to-blind-xxe
