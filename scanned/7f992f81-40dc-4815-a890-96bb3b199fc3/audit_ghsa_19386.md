# [C] Rancher: Restricted Administrator can change Administrator's passwords

## Summary
Severity: Critical
Advisory: GHSA-8p83-cpfg-fj3g
CVE: CVE-2025-23391
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-8p83-cpfg-fj3g
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.8.0 <2.8.14
- Go: `github.com/rancher/rancher` — affected >=2.9.0 <2.9.8
- Go: `github.com/rancher/rancher` — affected >=2.10.0 <2.10.4

## Details
### Impact
A vulnerability has been identified within Rancher where a Restricted Administrator can change the password of Administrators and take over their accounts. 

A Restricted Administrator should be not allowed to change the password of more privileged users unless it contains the Manage Users permissions.

Rancher deployments where the Restricted Administrator role is not being used are not affected by this CVE.
Please consult the associated  [MITRE ATT&CK - Technique - Abuse Elevation Control Mechanism](https://attack.mitre.org/techniques/T1548/) for further information about this category of attack.

### Patches
The fix introduces a few changes:
1. If the user has a manage-users verb, the user is allowed to edit/delete users. That way the Manage Users built in role will still be able to edit ALL users.
2. If the user doesn't have manage-users, just edit or delete, then there is a check to ensure that the User being edited only has rules equal to or less than the editor.

Patched versions include releases `v2.8.14`, `v2.9.8`, `v2.10.4` and `v2.11.0`

### Workarounds
Users are recommended to upgrade, as soon as possible, to a version of Rancher Manager that contains the fix.
If users can't upgrade, the following are recommended:
1. Limit access to Rancher Restricted Admin only to trusted users.
2. Downgrade Restricted Administrators to custom roles with limited permissions.

### Credits
This issue was identified and reported by Xavier Duthil from OVHcloud.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-8p83-cpfg-fj3g
- https://nvd.nist.gov/vuln/detail/CVE-2025-23391
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-23391
- https://github.com/rancher/rancher
