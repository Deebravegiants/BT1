# [H] Chartbrew: Incorrect Access Control in project share policy routes via unbound policy_id

## Summary
Severity: High
Advisory: CVE-2026-40600
Aliases: GHSA-pq8h-2h99-39xm
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-40600
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. In version 4.9.0, Chartbrew allows authenticated users with access to one project to update or delete a SharePolicy record that belongs to a different project. The affected routes authorize the caller against the project in the URL path, but they never verify that policy_id belongs to that project. This permits cross-project modification of dashboard sharing rules, including visibility, password requirements, allowed parameters, and expiration settings. This issue has been patched in version 5.0.0.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40600.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-pq8h-2h99-39xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40600
