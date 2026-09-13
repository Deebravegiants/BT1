# [H] Directus: TUS Upload Authorization Bypass Allows Arbitrary File Overwrite

## Summary
Severity: High
Advisory: GHSA-qqmv-5p3g-px89
CVE: CVE-2026-35412
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-qqmv-5p3g-px89
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.16.1

## Details
## Summary

Directus' TUS resumable upload endpoint (`/files/tus`) allows any authenticated user with basic file upload permissions to overwrite arbitrary existing files by UUID. The TUS controller performs only collection-level authorization checks, verifying the user has some permission on `directus_files`, but never validates item-level access to the specific file being replaced. As a result, row-level permission rules (e.g., "users can only update their own files") are completely bypassed via the TUS path while being correctly enforced on the standard REST upload path.

## Impact

- **Arbitrary file overwrite:** Any authenticated user with basic TUS upload permissions can overwrite any file in `directus_files` by UUID, regardless of row-level permission rules.
- **Permanent data loss:** The victim file's original stored bytes are deleted from storage and replaced with attacker-controlled content.
- **Metadata corruption:** The victim file's database record is updated with the attacker's filename, type, and size metadata.
Privilege escalation potential: If admin-owned files (e.g., application assets, templates) are stored in `directus_files`, a low-privilege user could replace them with malicious content.

## Workaround

Disable TUS uploads by setting `TUS_ENABLED=false` if resumable uploads are not required.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/directus/directus/security/advisories/GHSA-qqmv-5p3g-px89
- https://nvd.nist.gov/vuln/detail/CVE-2026-35412
- https://github.com/directus/directus
