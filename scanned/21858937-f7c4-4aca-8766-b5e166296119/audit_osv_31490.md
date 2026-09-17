# [H] Abrt: command-injection in abrt leading to local privilege escalation

## Summary
Severity: High
Advisory: CVE-2025-12744
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2025-12744
Type: osv

## Details
A flaw was found in the ABRT daemon’s handling of user-supplied mount information.ABRT copies up to 12 characters from an untrusted input and places them directly into a shell command (docker inspect %s) without proper validation. An unprivileged local user can craft a payload that injects shell metacharacters, causing the root-running ABRT process to execute attacker-controlled commands and ultimately gain full root privileges.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-12744
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12744.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-12744
- https://bugzilla.redhat.com/show_bug.cgi?id=2412467
- https://github.com/abrt/abrt
