# [C] Budibase has nonymous NoSQL operator injection via published-app query templates

## Summary
Severity: Critical
Advisory: GHSA-8qv3-p479-cj62
CVE: CVE-2026-54350
CWE: CWE-89, CWE-943
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-8qv3-p479-cj62
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.12

## Details
## Summary

`enrichContext` at `packages/server/src/sdk/workspace/queries/queries.ts:121-138` substitutes parameter values into the raw JSON body of a query, then `JSON.parse`s the result. The validator `validateQueryInputs` at `packages/server/src/api/controllers/query/index.ts:61-71` rejects only Handlebars markers (`{{`, `}}`) in user input and does not escape JSON metacharacters (`"`, `\`, `}`). A parameter value containing a closing quote and additional keys lifts attacker-controlled fields into the parsed filter object.

For Mongo `find`, the parsed filter passes directly to `collection.find()` (`packages/server/src/integrations/mongodb.ts:506-510`). Duplicate-key JSON parsing overrides the builder's `{name: "..."}` with `{name: {$exists: true}}` and returns every document. The same primitive against an `updateMany` query (`mongodb.ts:577-585`) widens the filter scope to the full collection while the builder-controlled `$set` body runs against every matched document.

The `authorized` middleware at `packages/server/src/middleware/authorized.ts:141-148` short-circuits when the query's role is `PUBLIC`. CSRF is not enforced on this path. `POST /api/v2/queries/:queryId` (`packages/server/src/api/routes/query.ts:63`) accepts the call with no session, only an `x-budibase-app-id` header that is public from the published-app URL.

Result: an unauthenticated visitor of any published Budibase app reads every document of the backing MongoDB, CouchDB, Elasticsearch, DynamoDB-PartiQL, or REST-with-JSON-body collection and, where the builder has published a PUBLIC write query, modifies every document of that collection with one HTTP request.

## Affected

`Budibase/budibase` server, `@budibase/server` package, `<= 3.39.0` (HEAD `feab995`, released 2026-05-20).

Reachable on any deployment where a workspace builder has set the role of a non-SQL query (MongoDB, CouchDB, Elasticsearch, DynamoDB-PartiQL, or REST with `bodyType=json`) to `PUBLIC` and published the app. This is the canonical low-code public-form use case.

SQL datasources (Postgres, MySQL, MSSQL, Oracle, MariaDB) route through `interpolateSQL` and are not affected.

## Root cause

`packages/server/src/sdk/workspace/queries/queries.ts:121-138`: `processStringSync(fields[key], parameters, {noEscaping: true, noHelpers: true})` writes the raw parameter value into the JSON-body string with no JSON-string escape; the followup `JSON.parse(enrichedQuery.json || enrichedQuery.customData || enrichedQuery.requestBody)` lifts the substituted text into the integration filter object.

`packages/server/src/api/controllers/query/index.ts:61-71`: `validateQueryInputs` only rejects values where `findHBSBlocks(value).length !== 0` (Handlebars markers) and ignores JSON metacharacters.

`packages/server/src/integrations/mongodb.ts:506-510`: `collection.find(json)` receives the user-controlled filter object directly with no key prefix or operator allow-list.

`packages/server/src/integrations/mongodb.ts:577-585`: `collection.updateMany(json.filter, json.update, json.options)` accepts the templated filter without verifying that the substituted filter still matches the builder's intent.

`packages/server/src/middleware/authorized.ts:141-148`: `if (resourceRoles.includes(roles.BUILTIN_ROLE_IDS.PUBLIC)) return next()` skips both authentication and CSRF.

`packages/server/src/integrations/queries/sql.ts:29-122`: `interpolateSQL` rewrites every `{{ binding }}` to a positional bind placeholder (`$N` or `?`). The SQL leg is bind-parameterised; the JSON leg is not.

## Reproduction

`budibase/budibase:latest` (`v3.39.0`) Docker single-container, default config. Builder logs in once, creates a MongoDB datasource, creates a query `GetUserByName` with body `{ "name": "{{ name }}" }`, sets the query role to `PUBLIC`, and publishes the app.

1. Anonymous client sends the inject payload to the read query.

```http
POST /api/v2/queries/<read-queryId> HTTP/1.1
Host: <budibase-host>
x-budibase-app-id: <published-appId>
Content-Type: application/json

{"parameters":{"name":"x\",\"name\":{\"$exists\":true},\"$comment\":\"audit"}}
```

```json
{"data":[
  {"_id":"...","name":"alice","secret":"alice-secret-flag"},
  {"_id":"...","name":"bob","secret":"bob-secret-flag"},
  {"_id":"...","name":"admin","role":"admin","secret":"ADMIN-SUPER-SECRET-FLAG"}
]}
```

2. Builder publishes a second query `TouchUser` (verb `update`, action `updateMany`, body `{ "filter": { "name": "{{ name }}" }, "update": { "$set": { "touched": true } } }`, role `PUBLIC`). Anonymous client sends the same inject pattern.

```http
POST /api/v2/queries/<updateMany-queryId> HTTP/1.1
Host: <budibase-host>
x-budibase-app-id: <published-appId>
Content-Type: application/json

{"parameters":{"name":"x\",\"name\":{\"$exists\":true},\"$comment\":\"esc"}}
```

```json
{"data":[{"acknowledged":true,"matchedCount":3,"modifiedCount":3,"upsertedId":null,"upsertedCount":0}]}
```

Live-verified: against Budibase v3.39.0 on 2026-05-20, anonymous read returned every document including `ADMIN-SUPER-SECRET-FLAG`; anonymous `updateMany` reported `matchedCount: 3, modifiedCount: 3` against a 3-document collection where the builder's filter intended `name = "x"`.

## Impact

- Anonymous read of every document in any backing MongoDB, CouchDB, Elasticsearch, DynamoDB-PartiQL, or REST-with-JSON-body collection reachable through a `PUBLIC` query, including columns the published query was not designed to return (`password_hash`, `secret`, `api_token`, `mfa_secret`).
- Anonymous modification of every document of that collection where the builder has published a `PUBLIC` `update`, `delete`, or `aggregate` query, beyond the builder's intended single-document scope.
- One HTTP request, no session, no CSRF, no user interaction.

## Credit

Jan Kahmen, [turingpoint](https://turingpoint.de) (jan@turingpoint.de).

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-8qv3-p479-cj62
- https://nvd.nist.gov/vuln/detail/CVE-2026-54350
- https://github.com/Budibase/budibase
