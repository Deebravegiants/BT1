# [C] Valtimo has SpEL injection via StandardEvaluationContext that allows Remote Code Execution by admin users

## Summary
Severity: Critical
Advisory: GHSA-j7j9-5253-f7vh
CVE: CVE-2026-42555
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-j7j9-5253-f7vh
Type: github-advisory

## Affected
- Maven: `com.ritense.valtimo:document` — affected >=12.0.0 <12.32.0
- Maven: `com.ritense.valtimo:case` — affected >=13.0.0 <13.23.0
- Maven: `com.ritense.valtimo:contract` — affected >=13.4.0 <13.23.0

## Details
### Summary

Multiple classes evaluate Spring Expression Language (SpEL) expressions from user-supplied input using `StandardEvaluationContext`, which provides unrestricted access to Java types and methods. An authenticated user with the ADMIN role can achieve Remote Code Execution and credential exfiltration.

### Impact

An attacker with ADMIN credentials can:
- **Execute arbitrary OS commands** via `T(java.lang.Runtime).getRuntime().exec('...')`
- **Exfiltrate all environment variables** (database passwords, API keys, Keycloak secrets) via `T(java.lang.System).getenv()`
- **Read JVM system properties** via `T(java.lang.System).getProperties()`
- **Load arbitrary classes** via `T(java.lang.Class).forName('...')`

### Affected Components

**1. DocumentMigrationService** (since 12.0.0)

Exploitable through the document migration REST API:
- `POST /api/management/v1/document-definition/migrate`
- `POST /api/management/v1/document-definition/migration/conflicts`

The malicious SpEL expression is supplied in the `source` or `target` field of a `DocumentMigrationPatch` object in the request body, using the `${...}` template syntax.

- In 12.x: `com.ritense.document.service.DocumentMigrationService#handleSpelExpression` (document module)
- In 13.x: same class, moved to the case module

**2. Condition** (since 13.4.0)

Exploitable through any admin-configured widget, dashboard, or feature that uses the `Condition` framework. The SpEL expression is supplied in the `value` field of a condition's JSON configuration.

- `com.ritense.valtimo.contract.conditions.Condition#resolveValue` (contract module)

This component has a significantly wider attack surface than DocumentMigrationService, as conditions are used across many modules.

### Remediation

Replace `StandardEvaluationContext` with `SimpleEvaluationContext` in both affected classes, which disallows Java type references and arbitrary method invocation:

```kotlin
val evaluationContext = SimpleEvaluationContext
    .forPropertyAccessors(MapAccessor(), jsonPropertyAccessor)
    .build()
```

## References
- https://github.com/valtimo-platform/valtimo/security/advisories/GHSA-j7j9-5253-f7vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-42555
- https://github.com/valtimo-platform/valtimo
