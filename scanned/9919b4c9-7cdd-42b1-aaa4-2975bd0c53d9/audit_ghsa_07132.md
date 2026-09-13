# [M] Kimai: Improper Authorization Through Activity Creation with Preset Project Allows Creation Under Unauthorized Projects

## Summary
Severity: Medium
Advisory: GHSA-3q6q-26vg-v97x
CVE: CVE-2026-52821
CWE: CWE-639, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-3q6q-26vg-v97x
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.57.0

## Details
### Summary

Kimai 2.56.0 contains an authenticated improper authorization vulnerability in the preset-project activity creation flow. A user with the generic `create_activity` permission, but without access to a target project, can still create a new `Activity` under that unauthorized project by visiting the preset project creation route directly.

This is a persistent cross-project business-object creation issue. The attacker does not need permission to view or edit the target project and only needs to know a valid `project.id`.

### Details

The issue affects the activity creation entry point that accepts a preset project identifier:

- `GET/POST /en/admin/activity/create/{project}`
- `GET/POST /en/admin/project/create/{customer}`

In `src/Controller/ActivityController.php`, the controller checks only the global capability to create activities and does not verify whether the current user is allowed to create an activity under the supplied `Project` object.

The form and repository path also preserve the preset project instead of rejecting it when the user lacks access.  Because the preset project is merged into the candidate set, the final save operation can persist a new `Activity` under a project that is outside the attacker's authorized project scope.

The same logic applies to the `src/Controller/ProjectController.php`.

*A PoC was provided, but removed for security reasons.*

### Impact

This vulnerability allows an authenticated user to inject new child business objects into projects outside their authorized scope. An attacker can pollute another team's project configuration, influence later timesheet selection and rate inheritance, and create conditions for downstream business abuse if other users start using the injected activity.

# Solution

- In `ActivityController` we now validate if the project can be edited with `[IsGranted('edit', 'project')]`
- In `ProjectController` we now validate if if the customer can be edited with `[IsGranted('edit', 'customer')]`

See https://www.kimai.org/en/security/ghsa-3q6q-26vg-v97x

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-3q6q-26vg-v97x
- https://github.com/kimai/kimai
- https://www.kimai.org/en/security/ghsa-3q6q-26vg-v97x
