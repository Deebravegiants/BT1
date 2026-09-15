# [H] Suricata is vulnerable to a heap buffer overflow on verdict

## Summary
Severity: High
Advisory: CVE-2025-64330
Aliases: GHSA-83v7-gm34-f437
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-64330
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. Prior to versions 7.0.13 and 8.0.2, a single byte read heap overflow when logging the verdict in eve.alert and eve.drop records can lead to crashes. This requires the per packet alert queue to be filled with alerts and then followed by a pass rule. This issue has been patched in versions 7.0.13 and 8.0.2. To reduce the likelihood of this issue occurring, the alert queue size a should be increased (packet-alert-max in suricata.yaml) if verdict is enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64330.json
- https://github.com/OISF/suricata/security/advisories/GHSA-83v7-gm34-f437
- https://nvd.nist.gov/vuln/detail/CVE-2025-64330
- https://github.com/OISF/suricata/commit/482e5eac9218d007adbe2410d6c00173368ce947
