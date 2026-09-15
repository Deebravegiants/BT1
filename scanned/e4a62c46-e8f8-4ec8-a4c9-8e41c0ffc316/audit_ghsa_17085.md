# [M] Ibexa Kernel's files with blacklisted extensions can be still saved to drafts

## Summary
Severity: Medium
Advisory: GHSA-mwvh-p3hx-x4gg
CWE: CWE-434
Ecosystem: Packagist
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-mwvh-p3hx-x4gg
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-kernel` — affected >=1.3.0 <1.3.35

## Details
### Impact
File validation can be configured to reject certain files by file type. When this happens, validation fails, and the content can't be published. However, the file can be saved when saving the content draft. This means unwanted files can be present in storage, even if they are not easily accessible due to the content not being published. The fix ensures these unwanted file types are never stored. An attacker would need to have existing access to create content with a file field type to exploit this.

### Patches
See "Patched versions".
Commit: https://github.com/ezsystems/ezplatform-kernel/commit/7e472317f7c75f45f72f74c38406952d8bea0de1

### References
https://developers.ibexa.co/security-advisories/ibexa-sa-2024-002-file-validation-and-workflow-stages

## References
- https://github.com/ezsystems/ezplatform-kernel/security/advisories/GHSA-mwvh-p3hx-x4gg
- https://github.com/ezsystems/ezplatform-kernel/commit/7e472317f7c75f45f72f74c38406952d8bea0de1
- https://developers.ibexa.co/security-advisories/ibexa-sa-2024-002-file-validation-and-workflow-stages
- https://github.com/ezsystems/ezplatform-kernel
