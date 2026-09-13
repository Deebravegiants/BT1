# [C] @fastify/aws-lambda vulnerable to Lambda event spoofing via client-controlled x-apigateway-event header

## Summary
Severity: Critical
Advisory: CVE-2026-18248
Aliases: GHSA-m93c-jj3f-68ph
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-18248
Type: osv

## Details
@fastify/aws-lambda version 6.4.0 decorates each Fastify request with request.awsLambda.event and request.awsLambda.context, values that applications are documented to use for authorization decisions such as reading API Gateway authorizer claims. In the default configuration, the getter that populates this decoration reads the client-controlled x-apigateway-event and x-apigateway-context HTTP headers before falling back to the trusted internal request token, and those reserved headers are not stripped from the incoming event. An unauthenticated attacker who can set a single HTTP header can therefore forge the entire Lambda proxy event, including the authorizer context, and override the genuine one. This results in a full authentication and authorization bypass and privilege escalation for any application that trusts request.awsLambda.event for identity or access control. Only version 6.4.0 is affected. Patches: upgrade to @fastify/aws-lambda 6.4.1, which resolves the decoration only through the internal per-invocation token and strips the reserved headers before the request is processed.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18248.json
- https://github.com/fastify/aws-lambda-fastify/security/advisories/GHSA-m93c-jj3f-68ph
- https://nvd.nist.gov/vuln/detail/CVE-2026-18248
