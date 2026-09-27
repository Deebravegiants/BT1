# [M] nocodb SQL Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3m5q-q39v-xf8f
CVE: CVE-2023-43794
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-3m5q-q39v-xf8f
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.111.0

## Details
## Summary

Nocodb contains SQL injection vulnerability, that allows an authenticated attacker with creator access to query the underlying database.

## Product

nocodb/nocodb

## Tested Version

[0.109.2](https://github.com/nocodb/nocodb/releases/tag/0.109.2)

## Details

### SQL injection in `SqliteClient.ts` (`GHSL-2023-141`)
By supplying a specially crafted payload to the given below parameter and endpoint, an attacker can inject arbitrary SQL queries to be executed. Since this is a blind SQL injections, an attacker may need to use time-based payloads which would include a function to delay execution for a given number of seconds. The response time indicates, whether the result of the query execution was true or false. Depending on the result, the HTTP response will be returned after a given number of seconds, indicating TRUE, or immediately, indicating FALSE. In that way, an attacker can reveal the data present in the database.

The [`triggerList`](https://github.com/nocodb/nocodb/blob/3ec82824eeb2295f6b67fd67e7d6049784b41221/packages/nocodb/src/db/sql-client/lib/sqlite/SqliteClient.ts#L628-L654) method creates a SQL query using the user-controlled [`table_name`](https://github.com/nocodb/nocodb/blob/3ec82824eeb2295f6b67fd67e7d6049784b41221/packages/nocodb/src/db/sql-client/lib/sqlite/SqliteClient.ts#L637) parameter value from the [`tableCreate`](https://github.com/nocodb/nocodb/blob/3ec82824eeb2295f6b67fd67e7d6049784b41221/packages/nocodb/src/controllers/tables.controller.ts#L63) endpoint.

```javascript
async triggerList(args: any = {}) {
  const _func = this.triggerList.name;
  const result = new Result();
  log.api(`${_func}:args:`, args);

  try {
    args.databaseName = this.connectionConfig.connection.database;

    const response = await this.sqlClient.raw(
      `select *, name as trigger_name from sqlite_master where type = 'trigger' and tbl_name='${args.tn}';`,
    );
[...]
```

#### Impact

This issue may lead to `Information Disclosure`.

## Credit

This issue was discovered and reported by GHSL team member [@sylwia-budzynska (Sylwia Budzynska)](https://github.com/sylwia-budzynska).


## Disclosure Policy

This report is subject to our [coordinated disclosure policy](https://securitylab.github.com/advisories#policy).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-3m5q-q39v-xf8f
- https://nvd.nist.gov/vuln/detail/CVE-2023-43794
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/blob/3ec82824eeb2295f6b67fd67e7d6049784b41221/packages/nocodb/src/controllers/tables.controller.ts#L63
- https://github.com/nocodb/nocodb/blob/3ec82824eeb2295f6b67fd67e7d6049784b41221/packages/nocodb/src/db/sql-client/lib/sqlite/SqliteClient.ts#L628-L654
- https://github.com/nocodb/nocodb/blob/3ec82824eeb2295f6b67fd67e7d6049784b41221/packages/nocodb/src/db/sql-client/lib/sqlite/SqliteClient.ts#L637
