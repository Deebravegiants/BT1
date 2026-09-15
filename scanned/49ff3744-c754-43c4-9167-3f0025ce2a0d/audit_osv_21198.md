# [H] CVE-2021-41144

## Summary
Severity: High
Advisory: CVE-2021-41144
Aliases: GHSA-5j2g-3ph4-rgvm
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-27
Source: https://osv.dev/vulnerability/CVE-2021-41144
Type: osv

## Details
OpenMage LTS is an e-commerce platform. Prior to versions 19.4.22 and 20.0.19, a layout block was able to bypass the block blacklist to execute remote code. Versions 19.4.22 and 20.0.19 contain a patch for this issue.

## References
- https://github.com/OpenMage/magento-lts/releases/tag/v19.4.22
- https://github.com/OpenMage/magento-lts/releases/tag/v20.0.19
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-5j2g-3ph4-rgvm
- https://github.com/OpenMage/magento-lts/commit/06c45940ba3256cdfc9feea12a3c0ca56d23acf8
