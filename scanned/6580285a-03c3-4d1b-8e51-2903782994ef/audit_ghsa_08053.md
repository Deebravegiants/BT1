# [M] Magento's X-Original-Url header can expose admin url

## Summary
Severity: Medium
Advisory: GHSA-jg68-vhv3-9r8f
CVE: CVE-2026-25523
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-jg68-vhv3-9r8f
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <20.16.1

## Details
### Impact

The admin url can be discovered without prior knowledge of it's location by exploiting the X-Original-Url header on some configurations.

### Patches

The bug comes from the Zend library and is patche by unsetting the header in the bootstrap process.

### Workarounds

Unset the `X-Original-Url` header in the web server configuration.

### References

The activation of these headers is coming from the Zend_Controller module. It appears this has been known to some degree since 2016 -
https://peterocallaghan.co.uk/2016/12/magento-poisoning-cache/ (dead link now..)

### Credit

Anees Hyder ( @anees0xdev ) via HackerOne
https://hackerone.com/anees0x_dev/hacktivity

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-jg68-vhv3-9r8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25523
- https://github.com/OpenMage/magento-lts
- https://hackerone.com/bugs?subject=openmage&report_id=3416312
