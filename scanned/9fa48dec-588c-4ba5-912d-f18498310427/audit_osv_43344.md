# [C] Semaphore U: OS Command Injection

## Summary
Severity: Critical
Advisory: CVE-2026-73294
Aliases: CVE-2026-73682, GHSA-xp7j-h7jc-4w8p, GO-2026-6435
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73294
Type: osv

## Details
Semaphore UI is a web interface for managing DevOps tools. Prior to 2.18.17 and 2.19.5-beta2, repository git_url handling passes an attacker-controlled --upload-pack option to CmdGitClient.GetLastRemoteCommitHash through POST /api/project/{id}/repositories and scheduled commit-hash polling, allowing a project Manager or Owner to execute arbitrary OS commands in the Semaphore server process. This issue is fixed in versions 2.18.17 and 2.19.5-beta2.

## References
- https://github.com/semaphoreui/semaphore/tree/v2.18.17
- https://github.com/semaphoreui/semaphore/tree/v2.19.5-beta2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73294.json
- https://github.com/semaphoreui/semaphore/security/advisories/GHSA-xp7j-h7jc-4w8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-73294
- https://github.com/semaphoreui/semaphore/commit/7e8a9434bd81b82cf42220151c74801ea97542d6
- https://github.com/semaphoreui/semaphore/commit/a7a7a33a64aea382a0726b3722856f298663eacf
