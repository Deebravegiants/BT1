# [M]  Kimai: Login CSRF in Default Team Creation Endpoints Allows Unauthorized Team and Permission Structure Changes

## Summary
Severity: Medium
Advisory: GHSA-pgcc-vfmc-7cw5
CVE: CVE-2026-49992
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-pgcc-vfmc-7cw5
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.58.0

## Details
### Summary

Kimai 2.56.0 contains authenticated cross-site request forgery issues in its default team creation shortcuts for projects, customers, and activities. These endpoints are exposed through `GET` routes and directly create or reuse a `Team`, add the current user as teamlead, and bind the target object to that team.

As a result, an attacker can trick a logged-in user with the required permissions into visiting a malicious page and cause unauthorized changes to team, teamlead, and object-binding relationships. This is a real authorization-structure modification issue rather than a harmless UI shortcut.

### Details

The issue affects at least the following routes:

- `GET /en/admin/project/{id}/create_team`
- `GET /en/admin/customer/{id}/create_team`
- `GET /en/admin/activity/{id}/create_team`

Each of these routes is a `GET` endpoint, yet each performs persistent writes that alter authorization structure:

- create or reuse a `Team`
- add the current user as `teamlead`
- bind the target `Project`, `Customer`, or `Activity` to that team

*A PoC was provided, but removed for security reasons.*

### Impact

This vulnerability allows an attacker to remotely alter permission topology while the victim is logged in. A successful exploit can create or reuse a team, assign the victim as its teamlead, and bind a project, customer, or activity to that team without intentional user action.

The pre-requisite is, that the logged-in user already has access to manage permissions of the object in question.

Because these routes modify authorization structure rather than a simple personal preference, the business impact can extend into visibility rules, assignment scope, team-based access control, reporting, and later privilege-expansion chains. This makes the issue materially more serious than a low-value cosmetic CSRF.

## Solution

- The routes have been moved to API `POST` endpoints

See https://www.kimai.org/en/security/ghsa-pgcc-vfmc-7cw5

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-pgcc-vfmc-7cw5
- https://github.com/kimai/kimai
- https://www.kimai.org/en/security/ghsa-pgcc-vfmc-7cw5
