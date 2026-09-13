# [M] Manyfold has IDOR in ModelFilesController

## Summary
Severity: Medium
Advisory: CVE-2026-28225
Aliases: GHSA-v8pw-3r2f-3fqm
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-28225
Type: osv

## Details
Manyfold is an open source, self-hosted web application for managing a collection of 3d models, particularly focused on 3d printing. Prior to version 0.133.1, the `get_model` method in `ModelFilesController` (line 158-160) loads models using `Model.find_param(params[:model_id])` without `policy_scope()`, bypassing Pundit authorization. All other controllers correctly use `policy_scope(Model).find_param()` (e.g., `ModelsController` line 263). Version 0.133.1 fixes the issue.

## References
- https://github.com/manyfold3d/manyfold/releases/tag/v0.133.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28225.json
- https://github.com/manyfold3d/manyfold/security/advisories/GHSA-v8pw-3r2f-3fqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-28225
