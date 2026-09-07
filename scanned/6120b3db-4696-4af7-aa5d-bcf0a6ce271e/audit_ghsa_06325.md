# [M] Craft CMS: Missing authorization check allows non-admin control panel users to reorder Global Sets

## Summary
Severity: Medium
Advisory: GHSA-9p7c-v5x3-rfx8
CVE: CVE-2026-14793
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-9p7c-v5x3-rfx8
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.18.1
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.3

## Details
The `reorder-sets` action in Craft CMS’s `GlobalsController` is missing the `requireAdmin()` check that the adjacent `save-set` and `delete-set` actions both enforce. Any authenticated control panel user can POST to `/actions/globals/reorder-sets` and permanently reorder all global sets in the project config, regardless of whether they have admin access. The reordering is written through to the project config and persists across requests.

## Description

`GlobalsController` exposes three administrative actions for managing global set structure. Two of them gate on admin status; the third does not.

## Prerequisites

- A Craft CMS instance with at least two global sets and a non-admin control panel user account.

## Impact

A non-admin control panel user can reorder all global sets. While this does not expose or modify content, reordering global sets modifies the project config -- a versioned artifact that is typically committed to source control and deployed across environments. An attacker can create noise in the project config history, trigger config-sync conflicts, or manipulate the display order seen by all editors in the admin panel. The same non-admin user cannot create or delete global sets because those actions correctly enforce `requireAdmin()`.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-9p7c-v5x3-rfx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-14793
- https://github.com/craftcms/cms/commit/9bd05c91e6a7e6da5e949ec41a31c220c059aa04
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.18.1
- https://github.com/craftcms/cms/releases/tag/5.10.3
- https://vuldb.com/cve/CVE-2026-14793
- https://vuldb.com/submit/850792
- https://vuldb.com/vuln/376387
