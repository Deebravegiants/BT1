# [M] Pimcore contains Unrestricted Upload of File with Dangerous Type

## Summary
Severity: Medium
Advisory: GHSA-8xv4-jj4h-qww6
CVE: CVE-2023-23937
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-02
Source: https://github.com/advisories/GHSA-8xv4-jj4h-qww6
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.16

## Details
### Impact
The upload functionality for updating user profile does not properly validate the file content-type, allowing any authenticated user to bypass this security check by adding a valid signature (p.e. GIF89) and sending any invalid content-type. This could allow an authenticated attacker to upload HTML files with JS content that will be executed in the context of the domain.

### Patches
Update to version 10.5.16 or apply this patch manually https://github.com/pimcore/pimcore/pull/14125.patch

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-8xv4-jj4h-qww6
- https://nvd.nist.gov/vuln/detail/CVE-2023-23937
- https://github.com/pimcore/pimcore/pull/14125
- https://github.com/pimcore/pimcore/commit/75a448ef8ac74424cf4e723afeb6d05f9eed872f
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/aa7ee076-d729-4fcc-9bcc-48bcbb8eac38
