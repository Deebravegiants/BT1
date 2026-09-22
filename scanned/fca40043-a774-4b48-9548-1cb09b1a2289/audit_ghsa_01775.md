# [H] Read permissions not enforced for client provided filter expressions in Elide.

## Summary
Severity: High
Advisory: GHSA-2mxr-89gf-rc4v
CVE: CVE-2020-5289
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-03-30
Source: https://github.com/advisories/GHSA-2mxr-89gf-rc4v
Type: github-advisory

## Affected
- Maven: `com.yahoo.elide:elide-core` — affected >=0 <4.5.14

## Details
### Impact
It is possible for an adversary to "guess and check" the value of a model field they do not have access to assuming they can read at least one other field in the model.  The adversary can construct filter expressions for an inaccessible field to filter a collection.  The presence or absence of models in the returned collection can be used to reconstruct the value of the inaccessible field.

For example, a User model has two fields: _name_ and _role_.  The adversary has read permissions to see the _name_ field of the User collection but not the _role_.  By constructing a filter like the one below, the adversary can determine which users have admin role by presence or absence in the returned collection:
`filter=role=="Admin"`

### Patches
Resolved in Elide 4.5.14 and greater.

### Workarounds
The adversary can only access the fields if a model includes fields with different read permission levels (some less secure and some more secure).  Model security can be adjusted by restricting read permissions on existing models.

### References
Fixed in https://github.com/yahoo/elide/pull/1236

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [elide](https://github.com/yahoo/elide)
* Contact us at [spectrum](https://spectrum.chat/elide?tab=posts)

## References
- https://github.com/yahoo/elide/security/advisories/GHSA-2mxr-89gf-rc4v
- https://nvd.nist.gov/vuln/detail/CVE-2020-5289
- https://github.com/yahoo/elide/pull/1236
- https://github.com/yahoo/elide/pull/1236/commits/a985f0f9c448aabe70bc904337096399de4576dc
