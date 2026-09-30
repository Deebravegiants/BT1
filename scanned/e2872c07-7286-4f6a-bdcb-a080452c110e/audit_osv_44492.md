# [M] ETS and Mnesia data layers overwrite an existing record on create instead of enforcing primary-key uniqueness

## Summary
Severity: Medium
Advisory: CVE-2026-82745
Aliases: EEF-CVE-2026-82745, GHSA-92x7-q3h5-wf88
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82745
Type: osv

## Details
Improper Access Control vulnerability in ash-project ash lets a create action overwrite an existing record when the ETS or Mnesia data layer is used, because neither enforced primary-key uniqueness on insert.

Unlike a SQL data layer, whose unique primary-key constraint rejects a duplicate, the ETS and Mnesia data layers implemented create as a keyed insert that replaces any existing entry with the same primary key (lib/ash/data_layer/ets/ets.ex, lib/ash/data_layer/mnesia/mnesia.ex). An actor who can set the primary key on a create (for example a user-supplied string or integer key) can submit a create whose key matches an existing record and silently overwrite it, destroying and replacing another entity's data without going through the update action or its policies. The fix rejects a create whose primary key already exists with an already-taken error, and only allows duplicates for keyless resources.

This issue affects ash: from 0.4.0 before 3.32.2.

## References
- https://cna.erlef.org/cves/CVE-2026-82745.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82745
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82745.json
- https://github.com/ash-project/ash/security/advisories/GHSA-92x7-q3h5-wf88
- https://nvd.nist.gov/vuln/detail/CVE-2026-82745
- https://github.com/ash-project/ash/commit/912e243196017c2a812c25905c2b1cc3bbb843fc
- https://github.com/ash-project/ash
