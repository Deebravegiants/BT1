# [M] Directus Vulnerable to Information Leakage in Existing Collections

## Summary
Severity: Medium
Advisory: GHSA-cph6-524f-3hgr
CVE: CVE-2025-64749
CWE: CWE-203, CWE-209
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-cph6-524f-3hgr
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.13.0
- npm: `@directus/api` — affected >=0 <32.0.0

## Details
### Summary:

An observable difference in error messaging was found in the Directus REST API. The `/items/{collection}` API returns different error messages for these two cases:
1. A user tries to access an existing collection which they are not authorized to access.
2. A user tries to access a non-existing collection.

The two differing error messages leak the existence of collections to users which are not authorized to access these collections.

### Details:

The following response returns an error message, when requesting a collection the user is not authorized to access.

```
GET /items/no-access
{
  "errors": [
    {
      "message": "You don't have permission to access collection \"no-access\" or it does not exist. Queried in root.",
      "extensions": {
        "reason": "You don't have permission to access collection \"no-access\" or it does not exist. Queried in root.",
        "code": "FORBIDDEN"
      }
    }
  ]
}
```

The following response returns a different error message when requesting a collection which does not exist.

```
GET /items/does-not-exist
{
  "errors": [
    {
      "message": "You don't have permission to access this.",
      "extensions": {
        "code": "FORBIDDEN"
      }
    }
  ]
}
```

### Impact:

The difference in errors between non-existent collections and collections blocked by permissions leak the existence of a collection to a user which is not authorized to access this object.

### Credit:

Sebastian Krause - [Hackmanit GmbH](https://hackmanit.de)

## References
- https://github.com/directus/directus/security/advisories/GHSA-cph6-524f-3hgr
- https://nvd.nist.gov/vuln/detail/CVE-2025-64749
- https://github.com/directus/directus/commit/f99c9b89071f9d136cc9b0d0c182f2d24542bc31
- https://github.com/directus/directus
