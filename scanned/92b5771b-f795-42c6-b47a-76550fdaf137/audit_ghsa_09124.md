# [M] MantisBT Vulnerable to Privilege Escalation from Manager to Administrator

## Summary
Severity: Medium
Advisory: GHSA-frf7-jhp9-jxm6
CVE: CVE-2026-34390
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-frf7-jhp9-jxm6
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
Insufficient access control checks in _ProjectUsersAddCommand_ (used in *manage_proj_user_add.php* and REST API endpoint `PUT /project/{id}/users`) allows users having *manage_project_threshold* access level (*manager* by default) to grant project-level *administrator* access to any user (including themselves) in any Project they have *manager* rights in.

The normal project-user add form does restrict the selectable access levels to the actor's own project role or below. However, the backend handler still accepts a forged higher access_level value and writes it.

### Impact
Privilege escalation.

The consequences of the privilege escalation are not as bad as it may sound, because having *administrator* access at Project level is effectively not very different from being *manager*, it does not actually give administrator privileges on the whole MantisBT instance. In particular, it does not let the upgraded user delete the Project or grant them any access to global administrative functions such as managing Users, Projects, Plugins, Custom Fields, etc. 

### Patches
- 69e0180f180ed5acf48a8d281a73683a7bf32461

### Workarounds
None

### Credits
Thanks to the following security researchers for independently discovering and responsibly reporting the issue:
- [Dracosec Research Limited](https://dracosec.tech/) (Siu Nam Tang, Chris Chan, Krecendo Hui, William Lam)
- Vishal Shukla

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-frf7-jhp9-jxm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-34390
- https://github.com/mantisbt/mantisbt/commit/69e0180f180ed5acf48a8d281a73683a7bf32461
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36995
- https://mantisbt.org/bugs/view.php?id=37002
