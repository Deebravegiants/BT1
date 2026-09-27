# [M] Snipe-IT has incorrect permission for legacy license checkin API 

## Summary
Severity: Medium
Advisory: GHSA-8frh-vhgh-64cf
CVE: CVE-2026-55479
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-8frh-vhgh-64cf
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
The legacy single-seat license checkin flow authorizes the action with the `checkout` permission instead of the `checkin` permission. Because of this, a user who is allowed to assign licenses but not unassign them can still directly access the old checkin endpoint and reclaim a license seat that is currently assigned to another user or asset.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-8frh-vhgh-64cf
- https://nvd.nist.gov/vuln/detail/CVE-2026-55479
- https://github.com/grokability/snipe-it/commit/80c8aa41dc813b0815db00bb44eb0fff9f89a227
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
