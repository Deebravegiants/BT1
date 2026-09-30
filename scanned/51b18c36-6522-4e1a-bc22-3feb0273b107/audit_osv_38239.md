# [M] InvenTree has SSTI in PART_NAME_FORMAT bypasses CVE-2026-27629 fix via {% if part.pk %} sandbox escape

## Summary
Severity: Medium
Advisory: CVE-2026-35477
Aliases: GHSA-84jh-x777-8pqq
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-35477
Type: osv

## Details
InvenTree is an Open Source Inventory Management System. From 1.2.3 to 1.2.6, the fix for CVE-2026-27629 upgraded the PART_NAME_FORMAT validator to use jinja2.sandbox.SandboxedEnvironment. However, the actual renderer in part/helpers.py was not updated and still uses the non-sandboxed jinja2.Environment. Additionally, the validator uses a dummy Part instance with pk=None, which allows conditional template expressions to behave differently during validation versus production rendering. A staff user with settings access can craft a template that passes validation but executes arbitrary code during rendering. This issue requires access by a user with granted staff permissions. This vulnerability is fixed in 1.2.7 and 1.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35477.json
- https://github.com/inventree/InvenTree/security/advisories/GHSA-84jh-x777-8pqq
- https://nvd.nist.gov/vuln/detail/CVE-2026-35477
