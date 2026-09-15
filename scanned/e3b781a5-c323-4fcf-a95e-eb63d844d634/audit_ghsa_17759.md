# [H] Zot IdP group membership revocation ignored

## Summary
Severity: High
Advisory: GHSA-c9p4-xwr9-rfhx
CVE: CVE-2025-23208
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-01-17
Source: https://github.com/advisories/GHSA-c9p4-xwr9-rfhx
Type: github-advisory

## Affected
- Go: `zotregistry.dev/zot` — affected >=0 <2.1.2

## Details
### Summary
The group data stored for users in the boltdb database (meta.db) is an append-list so group revocations/removals are ignored in the API.

### Details
[SetUserGroups](https://github.com/project-zot/zot/blob/5e30fec65c49e3139907e2819ccb39b2e3bd784e/pkg/meta/boltdb/boltdb.go#L1665) is alled on login, but instead of replacing the group memberships, they are appended. This may be due to some conflict with the group definitions in the config file, but that wasn't obvious to me if it were the case.

### PoC
Login with group claims, logout, remove the user from a group from at IdP and log in again, the API still grants access and the new list of groups is appended creating meaningless duplicate entries and no longer mathing the expected groups from the IdP. The behavior can be verified by seeing the API or UI still presenting images it should not or by viewing the data directly:  `bbolt get meta.db UserData <user>`, eg:

![image](https://github.com/user-attachments/assets/3491cbd2-c7d9-414d-bc33-3efc35ed0582)

Note this example also has duplicates due to group hierarchy changes that were left in the database.

### Impact
Any Zot configuration that relies on group-based authorization will not respect group remove/revocation by an IdP.

## References
- https://github.com/project-zot/zot/security/advisories/GHSA-c9p4-xwr9-rfhx
- https://nvd.nist.gov/vuln/detail/CVE-2025-23208
- https://github.com/project-zot/zot/commit/002ac62d8a15bf0cba010b3ba7bde86f9837b613
- https://github.com/project-zot/zot
- https://github.com/project-zot/zot/blob/5e30fec65c49e3139907e2819ccb39b2e3bd784e/pkg/meta/boltdb/boltdb.go#L1665
