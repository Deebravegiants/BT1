# [H] Autolab Misconfigured Reset Password Permissions

## Summary
Severity: High
Advisory: GHSA-v46j-h43h-rwrm
CVE: CVE-2024-49376
CWE: CWE-287, CWE-863
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-25
Source: https://github.com/advisories/GHSA-v46j-h43h-rwrm
Type: github-advisory

## Affected
- RubyGems: `Autolab` — affected >=3.0.0 <3.0.1

## Details
### Impact
For email-based accounts, users with insufficient privileges could reset and theoretically access privileged users' accounts by resetting their passwords.

### Patches
This is fixed in v3.0.1.

### Workarounds
No workarounds.

### For more information
If you have any questions or comments about this advisory:

Open an issue in https://github.com/autolab/Autolab/
Email us at [autolab-dev@andrew.cmu.edu](mailto:autolab-dev@andrew.cmu.edu)

## References
- https://github.com/autolab/Autolab/security/advisories/GHSA-v46j-h43h-rwrm
- https://nvd.nist.gov/vuln/detail/CVE-2024-49376
- https://github.com/autolab/Autolab/commit/301689ab5c5e39d13bab47b71eaf8998d04bcc9b
- https://github.com/autolab/Autolab
