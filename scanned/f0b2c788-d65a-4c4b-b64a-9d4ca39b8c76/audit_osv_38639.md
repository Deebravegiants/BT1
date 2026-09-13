# [M] EspoCRM: Broken Access Control / IDOR in Note Pinning API allows unauthorized modification of notes

## Summary
Severity: Medium
Advisory: CVE-2026-41160
Aliases: GHSA-c3rm-m24p-255p
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-41160
Type: osv

## Details
EspoCRM is an open source customer relationship management application. Prior to 9.3.5, a business logic flaw (Broken Access Control) in EspoCRM 9.3.3 allows low-privileged users to pin arbitrary notes without having the required edit permissions for the parent object. Due to a "write first, authorize later" execution flaw in the backend API, even though the server correctly returns a 403 Forbidden error, the targeted note's pinned status is already persistently modified in the database. The root cause lies in the server-side processing of the POST /api/v1/Note/{id}/pin endpoint. In application/Espo/Tools/Stream/Api/PostNotePin.php, the process() method first calls getNote($id) before calling checkParent($note). This vulnerability is fixed in 9.3.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41160.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-c3rm-m24p-255p
- https://nvd.nist.gov/vuln/detail/CVE-2026-41160
