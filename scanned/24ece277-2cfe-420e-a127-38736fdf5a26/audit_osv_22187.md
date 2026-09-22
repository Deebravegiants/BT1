# [M] Out of Bounds Read in OpenRazer Driver

## Summary
Severity: Medium
Advisory: CVE-2022-23467
Aliases: GHSA-39hg-jvc9-fg7h
CVSS: 4.4 (CVSS:3.1/AV:P/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:L)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/CVE-2022-23467
Type: osv

## Details
OpenRazer is an open source driver and user-space daemon to control Razer device lighting and other features on GNU/Linux. Using a modified USB device an attacker can leak stack addresses of the `razer_attr_read_dpi_stages`, potentially bypassing KASLR. To exploit this vulnerability an attacker would need to access to a users keyboard or mouse or would need to convince a user to use a modified device. The issue has been patched in v3.5.1. Users are advised to upgrade and should be reminded not to plug in unknown USB devices.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00032.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23467.json
- https://github.com/openrazer/openrazer/security/advisories/GHSA-39hg-jvc9-fg7h
- https://nvd.nist.gov/vuln/detail/CVE-2022-23467
- https://github.com/openrazer/openrazer/commit/33aa7f07d54ae066f201c6d298cb4a2181cb90e6
