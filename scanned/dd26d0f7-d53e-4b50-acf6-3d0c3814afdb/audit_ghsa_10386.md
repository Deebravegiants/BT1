# [C] ChilliCream GraphQL Platform: Utf8GraphQLParser Stack Overflow via Deeply Nested GraphQL Documents

## Summary
Severity: Critical
Advisory: GHSA-qr3m-xw4c-jqw3
CVE: CVE-2026-40324
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-qr3m-xw4c-jqw3
Type: github-advisory

## Affected
- NuGet: `HotChocolate.Language` — affected >=0 <12.22.7
- NuGet: `HotChocolate.Language` — affected >=13.0.0 <13.9.16
- NuGet: `HotChocolate.Language` — affected >=14.0.0 <14.3.1
- NuGet: `HotChocolate.Language` — affected >=15.0.0 <15.1.14

## Details
### Impact

Hot Chocolate's `Utf8GraphQLParser` is a recursive descent parser with no recursion depth limit. A crafted GraphQL document with deeply nested selection sets, object values, list values, or list types can trigger a `StackOverflowException` on payloads as small as **40 KB**.

Because `StackOverflowException` is **uncatchable in .NET** (since .NET 2.0), the entire worker process is terminated immediately. All in-flight HTTP requests, background `IHostedService` tasks, and open WebSocket subscriptions on that worker are dropped. The orchestrator (Kubernetes, IIS, etc.) must restart the process.

This occurs **before any validation rules run** — `MaxExecutionDepth`, complexity analyzers, persisted query allow-lists, and custom `IDocumentValidatorRule` implementations cannot intercept the crash because `Utf8GraphQLParser.Parse` is invoked before validation. The existing `MaxAllowedFields=2048` limit does not help because the crashing payloads contain very few fields.

**Severity:** Critical (9.1) — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H`

### Patches

- **v12 line:** Fixed in `12.22.7`
- **v13 line:** Fixed in `13.9.16`
- **v14 line:** Fixed in `14.3.1`
- **v15 line:** Fixed in `15.1.14`

The fix adds a `MaxAllowedRecursionDepth` option to `ParserOptions` with a safe default, and enforces it across all recursive parser methods (`ParseSelectionSet`, `ParseValueLiteral`, `ParseObject`, `ParseList`, `ParseTypeReference`, etc.). When the limit is exceeded, a catchable `SyntaxException` is thrown instead of overflowing the stack.

### Workarounds

There is no application-level workaround. `StackOverflowException` cannot be caught in .NET. The only mitigation is to upgrade to a patched version.

Operators can reduce (but not eliminate) risk by limiting HTTP request body size at the reverse proxy or load balancer layer, though the smallest crashing payload (40 KB) is well below most default body size limits and is highly compressible (~few hundred bytes via gzip).

### References

- Fix for v15: https://github.com/ChilliCream/graphql-platform/pull/9528

## References
- https://github.com/ChilliCream/graphql-platform/security/advisories/GHSA-qr3m-xw4c-jqw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-40324
- https://github.com/ChilliCream/graphql-platform/pull/9528
- https://github.com/ChilliCream/graphql-platform/pull/9530
- https://github.com/ChilliCream/graphql-platform/pull/9531
- https://github.com/ChilliCream/graphql-platform/commit/08c0caa42ca33c121bbed49d2db892e5bf6fb541
- https://github.com/ChilliCream/graphql-platform/commit/4cbaf67d366f800fc1e484bc5c06dfcf27b45023
- https://github.com/ChilliCream/graphql-platform/commit/b185eb276c9ee227bd44616ff113be7f01a66c69
- https://github.com/ChilliCream/graphql-platform/commit/b9271e6a500484c002fd528dcd34d1a9b445480f
- https://github.com/ChilliCream/graphql-platform
- https://github.com/ChilliCream/graphql-platform/releases/tag/12.22.7
- https://github.com/ChilliCream/graphql-platform/releases/tag/13.9.16
- https://github.com/ChilliCream/graphql-platform/releases/tag/14.3.1
- https://github.com/ChilliCream/graphql-platform/releases/tag/15.1.14
