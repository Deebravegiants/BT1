# [H] Strapi Allows Unauthorized Access to Private Fields via parms.lookup

## Summary
Severity: High
Advisory: GHSA-495j-h493-42q2
CVE: CVE-2024-56143
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-495j-h493-42q2
Type: github-advisory

## Affected
- npm: `@strapi/core` — affected >=5.0.0 <5.5.2

## Details
### Summary
It's possible to access any private fields by filtering through the lookup parameters

### Details

Using the new lookup operator provided by the document service in Strapi 5, it is not properly sanitizing this query operator for private fields.

### PoC

1. Create a strapi app.
2. Create a content-type
3. In the content-type you make a new entry
4. Go back to the list view
4. Add `&lookup[updatedBy][password][$startsWith]=$2` to the end of your url (All passwords start with $2) see that all entries are still there
6. Add `&lookup[updatedBy][password][$startsWith]=$3` see the entry disappear proving that the search above works

### Impact

An attacker can perform filtering attacks on everything related to the object, including admin passwords and reset-tokens. This means that they can gain full access to the strapi instance.

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-495j-h493-42q2
- https://nvd.nist.gov/vuln/detail/CVE-2024-56143
- https://github.com/strapi/strapi/commit/0c6e0953ae1e62afae9329de7ae6d6a5e21b95b8
- https://github.com/strapi/strapi
