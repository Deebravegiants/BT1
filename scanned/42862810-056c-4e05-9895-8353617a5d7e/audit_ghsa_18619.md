# [M] InventoryGui allows item duplication in GUIs which use GuiStorageElement

## Summary
Severity: Medium
Advisory: GHSA-7whh-79j3-7c55
CVE: CVE-2025-62784
CWE: CWE-837
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-7whh-79j3-7c55
Type: github-advisory

## Affected
- Maven: `de.themoep:inventorygui` — affected >=0 <1.6.5

## Details
### Impact
Any plugin using a GUI with the GuiStorageElement and allows taking out items out of that element.

### Patches
InventoryGui 1.6.5 (included in latest 1.6.5-SNAPSHOT) by disabling GuiStorageElement when not running on 1.21.9 or later.

### Workarounds
Not using the GuiStorageElement.

## References
- https://github.com/Phoenix616/InventoryGui/security/advisories/GHSA-7whh-79j3-7c55
- https://nvd.nist.gov/vuln/detail/CVE-2025-62784
- https://github.com/Phoenix616/InventoryGui/commit/690fc91d137c6cc04f6ed3a89449050964dd8cb9
- https://github.com/Phoenix616/InventoryGui
