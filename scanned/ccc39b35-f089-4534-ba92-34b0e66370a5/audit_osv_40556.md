# [H] LeafWiki Vulnerable to Privilege Escalation via User Self-Service Update

## Summary
Severity: High
Advisory: CVE-2026-53527
Aliases: GHSA-jj4r-587p-r5h5
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-53527
Type: osv

## Details
LeafWiki is a self-hosted wiki. Versions 0.1.0 through 0.10.0 have a privilege escalation vulnerability in the user update API. An authenticated user could update their own account role and escalate privileges from a regular user, such as `viewer`, to `admin`. Exploitation requires a valid authenticated LeafWiki user account. Instances without public registration and with only trusted users are at lower practical risk. Users should update to version 0.10.1 or greater. Until a patch is available, operators should restrict account creation and ensure that only trusted users have accounts on affected LeafWiki instances. If possible, access to the user update API should be restricted to trusted users or administrators only.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53527.json
- https://github.com/perber/leafwiki/security/advisories/GHSA-jj4r-587p-r5h5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53527
