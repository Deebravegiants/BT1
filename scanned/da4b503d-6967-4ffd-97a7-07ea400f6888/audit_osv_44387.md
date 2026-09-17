# [M] Flowintel Missing Task-to-Case Authorization Allows Cross-Case Task Modification

## Summary
Severity: Medium
Advisory: CVE-2026-81817
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81817
Type: osv

## Details
Affected versions of Flowintel contain an insecure direct object reference / broken object-level authorization issue across numerous task endpoints.


The routes generally received both a case identifier and a task identifier, but previously they did not enforce that the task actually belonged to the supplied case. As a result, an authenticated user with editor-level access to one case could potentially substitute the ID of a task from another case and invoke operations against that foreign task.


The patch introduces task_case_bound_required, which loads both objects and returns 404 unless the task belongs to the requested case. This protection is applied to edit, delete, note, assignment, status, file, export, MISP-linking, subtask, external-reference, and other task-related endpoints.

The fix also adds explicit checks that a requested note_id belongs to the current task before returning or exporting it, closing related cross-object access paths.

Version impacted =>3.3.0

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81817.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81817
- https://github.com/flowintel/flowintel/commit/10676eec7f1286d7ee0769546c772c5cb9c1c72b.patch
- https://github.com/flowintel/flowintel
