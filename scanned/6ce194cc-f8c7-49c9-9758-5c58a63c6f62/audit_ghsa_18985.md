# [M] Directus has Improper Permission Handling on Deleted Fields

## Summary
Severity: Medium
Advisory: GHSA-9x5g-62gj-wqf2
CVE: CVE-2025-64746
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-9x5g-62gj-wqf2
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.13.0

## Details
### Summary
Directus does not properly clean up field-level permissions when a field is deleted. If a new field with the same name is created later, the system automatically re-applies the old permissions, which can lead to unauthorized access.

### Details
When a field is removed from a collection, its reference in the permissions table remains intact. This stale reference creates a security gap: if another field is later created using the same name, it inherits the outdated permission entry.  
This behavior can unintentionally grant roles access to data they should not be able to read or modify.

The issue is particularly risky in multi-tenant or production environments, where administrators may reuse field names, assuming old permissions have been fully cleared.

	1.	Create a collection named test_collection.
	2.	Add a field called secret_field.
	3.	Assign a role with read permissions specifically tied to secret_field.
	4.	Remove the secret_field from the collection.
	5.	Create a new field with the exact same name secret_field.
	6.	Notice that the previously assigned permissions are still active, granting access to the newly created field without reconfiguration.

### Impact

When creating new fields with the same name as previously deleted fields it may inherit the permissions of that previously deleted field. This can potentially result in accidentally giving access to this new field in existing policies.

## References
- https://github.com/directus/directus/security/advisories/GHSA-9x5g-62gj-wqf2
- https://nvd.nist.gov/vuln/detail/CVE-2025-64746
- https://github.com/directus/directus/commit/84d7636969083387164ce5d2fd15a65e11e2d0b8
- https://github.com/directus/directus
