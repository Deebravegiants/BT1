# [M] Incorrect Permission Checking for GraphQL Subscriptions

## Summary
Severity: Medium
Advisory: GHSA-gggm-66rh-pp98
CVE: CVE-2023-38503
CWE: CWE-200, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-gggm-66rh-pp98
Type: github-advisory

## Affected
- npm: `directus` — affected >=10.3.0 <10.5.0

## Details
### Summary

CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
Access to information you should not have access to when the permissions rely on `$CURRENT_USER` for filtering.

### Details

The permission filters (i.e. `user_created IS $CURRENT_USER`) are not properly checked when using GraphQL subscription resulting in unauthorized users getting event on their subscription which they should not be receiving according to the permissions.
This can be any collection but out-of-the box the `directus_users` collection is configured with such a permissions filter allowing you to get updates for other users when changes happen.

An example:
```graphql
subscription {
  directus_users_mutated {
    event
    data {
      id
      last_access
      last_page
    }
  }
}
```

### Patches
https://github.com/directus/directus/pull/19155

### Workarounds
Disable GraphQL Subscriptions

### References

## References
- https://github.com/directus/directus/security/advisories/GHSA-gggm-66rh-pp98
- https://nvd.nist.gov/vuln/detail/CVE-2023-38503
- https://github.com/directus/directus/pull/19155
- https://github.com/directus/directus
