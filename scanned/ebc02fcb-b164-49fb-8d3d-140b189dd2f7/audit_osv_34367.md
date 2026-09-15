# [M] Himmelblau vulnerable to GID collision via group name-derived mapping (privilege escalation)

## Summary
Severity: Medium
Advisory: CVE-2025-59044
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-59044
Type: osv

## Details
Himmelblau is an interoperability suite for Microsoft Azure Entra ID and Intune. Himmelblau 0.9.x derives numeric GIDs for Entra ID groups from the group display name when himmelblau.conf `id_attr_map = name` (the default configuration). Because Microsoft Entra ID allows multiple groups with the same `displayName` (including end-user–created personal/O365 groups, depending on tenant policy), distinct directory groups can collapse to the same numeric GID on Linux. This issue only applies to Himmelblau versions 0.9.0 through 0.9.22. Any resource or service on a Himmelblau-joined host that enforces authorization by numeric GID (files/dirs, etc.) can be unintentionally accessible to a user who creates or joins a different Entra/O365 group that happens to share the same `displayName` as a privileged security group. Users should upgrade to 0.9.23, or 1.0.0 or later, to receive a patch. Group to GID mapping now uses Entra ID object IDs (GUIDs) and does not collide on same-name groups. As a workaround, use tenant policy hardening to restrict arbitrary group creation until all hosts are patched.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59044.json
- https://github.com/himmelblau-idm/himmelblau/security/advisories/GHSA-2m43-mmg9-3rgc
- https://github.com/himmelblau-idm/himmelblau/security/advisories/GHSA-gcxr-m95v-qcf7
- https://nvd.nist.gov/vuln/detail/CVE-2025-59044
- https://github.com/himmelblau-idm/himmelblau/commit/76c5b41df7f89378af65dc7c0d0484d7d41b3281
