# [H] Runtipi is Vulnerable to Authenticated Arbitrary Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-24129
Aliases: GHSA-vrgf-rcj5-6gv9
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-24129
Type: osv

## Details
Runtipi is a Docker-based, personal homeserver orchestrator that facilitates multiple services on a single server. Versions 3.7.0 and above allow an authenticated user to execute arbitrary system commands on the host server by injecting shell metacharacters into backup filenames. The BackupManager fails to sanitize the filenames of uploaded backups. The system persists user-uploaded files directly to the host filesystem using the raw originalname provided in the request. This allows an attacker to stage a file containing shell metacharacters (e.g., $(id).tar.gz) at a predictable path, which is later referenced during the restore process. The successful storage of the file is what allows the subsequent restore command to reference and execute it. This issue has been fixed in version 4.7.0.

## References
- https://github.com/runtipi/runtipi/releases/tag/v4.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24129.json
- https://github.com/runtipi/runtipi/security/advisories/GHSA-vrgf-rcj5-6gv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24129
- https://github.com/runtipi/runtipi/commit/c3aa948885554a370d374692158a3bfe1cfdc85a
