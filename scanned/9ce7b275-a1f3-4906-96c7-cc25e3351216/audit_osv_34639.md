# [M] InventoryGUI vulnerable to item duplication via Bundle items when using GuiStorageElement

## Summary
Severity: Medium
Advisory: CVE-2025-62782
Aliases: GHSA-rgvh-4m82-fvjq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:N/VI:H/VA:L/SC:N/SI:L/SA:L)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/CVE-2025-62782
Type: osv

## Details
InventoryGui is a library for creating chest GUIs for Bukkit/Spigot plugins. Versions 1.6.3-SNAPSHOT and earlier contain a vulnerability where GUIs using GuiStorageElement can allow item duplication when the experimental Bundle item feature is enabled on the server. The vulnerability is resolved in version 1.6.4-SNAPSHOT.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62782.json
- https://github.com/Phoenix616/InventoryGui/security/advisories/GHSA-rgvh-4m82-fvjq
- https://nvd.nist.gov/vuln/detail/CVE-2025-62782
- https://github.com/Phoenix616/InventoryGui/issues/51
- https://github.com/Phoenix616/InventoryGui/commit/00e684bd689ebc60bcb5b83ce4ef3c5a01778494
