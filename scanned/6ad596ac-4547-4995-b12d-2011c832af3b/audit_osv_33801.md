# [H] Lychee Path Traversal Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-50202
Aliases: GHSA-6rj9-gm78-vhf9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-50202
Type: osv

## Details
Lychee is a free photo-management tool. In versions starting from 6.6.6 to before 6.6.10, an attacker can leak local files including environment variables, nginx logs, other user's uploaded images, and configuration secrets due to a path traversal exploit in SecurePathController.php. This issue has been patched in version 6.6.10.

## References
- https://github.com/LycheeOrg/Lychee/blob/0709f5d984d4df77fc5e23a29a0231437e684e99/app/Http/Controllers/SecurePathController.php#L61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50202.json
- https://github.com/LycheeOrg/Lychee/security/advisories/GHSA-6rj9-gm78-vhf9
- https://nvd.nist.gov/vuln/detail/CVE-2025-50202
- https://github.com/LycheeOrg/Lychee/commit/ae7270b7b47e4a284ea1f69d260e52d592711072
