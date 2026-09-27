# [M] CVE-2026-50739

## Summary
Severity: Medium
Advisory: CVE-2026-50739
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-50739
Type: osv

## Details
A bypass for CVE‑2026‑34913 exists with proper ownership validation that had not been applied to the reverse operation of linking campaigns and trackers through the `tracker-campaigns.php` script in Revive Adserver 6.0.7 and earlier. As a result, a low‑privileged user could link their trackers to campaigns owned by other managers on the same instance, leading to inconsistent ownership relationships.

## References
- https://hackerone.com/reports/3780709
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50739.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50739
