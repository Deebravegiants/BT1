# [H] Communities and collections administrators can escalate their privilege up to system administrator

## Summary
Severity: High
Advisory: GHSA-cf2j-vf36-c6w8
CVE: CVE-2021-41189
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-01
Source: https://github.com/advisories/GHSA-cf2j-vf36-c6w8
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-api` — affected >=7.0 <7.1

## Details
### Impact
Any community or collection administrator can escalate their permission up to become system administrator.

This vulnerability only existed in 7.0 and does not impact 6.x or below.

### Patches
Fix is included in [7.1](https://github.com/DSpace/DSpace/releases/tag/dspace-7.1). Please upgrade to 7.1 at your earliest convenience.

### Workarounds
In 7.0, temporarily disable the ability for community or collection administrators to manage permissions or workflows settings, i.e. set the following properties in your local.cfg / dspace.cfg file
```
core.authorization.collection-admin.policies = false
core.authorization.community-admin.policies = false
core.authorization.community-admin.collection.workflows = false
```
Once upgraded to 7.1, these settings can be safely reverted to the default values of `true`.

### References
Discovered during investigation of https://github.com/DSpace/DSpace/issues/7928

### For more information
If you have any questions or comments about this advisory:
* Email us at security@dspace.org

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-cf2j-vf36-c6w8
- https://nvd.nist.gov/vuln/detail/CVE-2021-41189
- https://github.com/DSpace/DSpace/issues/7928
- https://github.com/DSpace/DSpace/commit/277b499a5cd3a4f5eb2370513a1b7e4ec2a6e041
- https://github.com/DSpace/DSpace/commit/c3bea16ab911606e15ae96c97a1575e1ffb14f8a
- https://github.com/DSpace/DSpace
