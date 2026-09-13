# [M] CVE-2026-77641

## Summary
Severity: Medium
Advisory: CVE-2026-77641
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77641
Type: osv

## Details
tor before 0.4.9.9 was prone to a NULL write after free when sending a CONFLUX_SWITCH cell fails. The return value of relay_send_command_from_edge() was   ignored, so a send failure (which calls circuit_mark_for_close()  and removes the leg via cfx_del_leg()) would go undetected, causing the caller to write to the now-freed current leg and resulting in a crash. This is TROVE-2026-017.

## References
- https://gitlab.torproject.org/tpo/core/tor/-/raw/tor-0.4.9.9/ChangeLog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77641.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77641
