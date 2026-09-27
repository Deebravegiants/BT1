# [H] Hono is Vulnerable to Authentication Bypass by IP Spoofing in AWS Lambda ALB conninfo

## Summary
Severity: High
Advisory: GHSA-xh87-mx6m-69f3
CVE: CVE-2026-27700
CWE: CWE-290, CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-xh87-mx6m-69f3
Type: github-advisory

## Affected
- npm: `hono` — affected >=4.12.0 <4.12.2

## Details
## Summary

When using the AWS Lambda adapter (`hono/aws-lambda`) behind an Application Load Balancer (ALB), the `getConnInfo()` function incorrectly selected the first value from the `X-Forwarded-For` header.

Because AWS ALB appends the real client IP address to the end of the `X-Forwarded-For` header, the first value can be attacker-controlled.

This could allow IP-based access control mechanisms (such as the `ipRestriction` middleware) to be bypassed.

## Details

In ALB environments, AWS appends the actual client IP address to the end of any existing `X-Forwarded-For` header value. However, the previous implementation of `getConnInfo()` extracted the leftmost IP address:

```ts
address = xff.split(',')[0].trim()
```

If a client sent:

```
X-Forwarded-For: <spoofed-ip>
```

ALB would forward:

```
X-Forwarded-For: <spoofed-ip>, <real-client-ip>
```

Since the implementation selected the first value, the spoofed IP address was trusted. This affected applications using:

```ts
ipRestriction(getConnInfo, { allowList: [...] })
```

or any custom middleware relying on `getConnInfo(c).remote.address` for authorization decisions.

The issue only affects deployments using the AWS Lambda adapter behind an ALB. API Gateway (v1/v2) and Lambda Function URLs are not affected, as they use AWS-provided source IP values from `requestContext`.

## Impact

An unauthenticated remote attacker could bypass IP-based access restrictions by supplying a crafted `X-Forwarded-For` header. This may allow access to resources that were intended to be restricted by IP address.

Only applications deployed behind an ALB and relying on `getConnInfo()` for IP-based authorization are affected.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-xh87-mx6m-69f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-27700
- https://github.com/honojs/hono/commit/41adbf56e252c04611f8972364ac0887ae07a4c7
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.2
