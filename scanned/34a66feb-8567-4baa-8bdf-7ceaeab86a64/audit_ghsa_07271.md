# [H] Quarkus: Authentication/Authorization Bypass via Advanced Path Normalization Vulnerabilities

## Summary
Severity: High
Advisory: GHSA-qcxp-gm7m-4j5v
CVE: CVE-2026-50559
CWE: CWE-178, CWE-287, CWE-41, CWE-551, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-qcxp-gm7m-4j5v
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=0 <3.20.6.2
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.21.0.CR1 <3.27.4.1
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.28.0.CR1 <3.33.2.1
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.34.0.CR1 <3.36.3
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.37.0.CR1 <3.37.0

## Details
Quarkus HTTP path-based authorization policies can be bypassed using encoded semicolons (%3B) to smuggle matrix
  parameters past the security layer, and using encoded slashes (%2F) or backslashes (%5C) to access protected static
  resources. This is a distinct issue from CVE-2026-39852, which addressed only literal semicolon stripping.

  ### Technical Details

  The security layer (AbstractPathMatchingHttpSecurityPolicy) normalizes request paths using Vert.x's normalizedPath(),
  which only decodes unreserved RFC 3986 characters (letters, digits, -, ., _, ~). It then strips matrix parameters by
  looking for literal ; characters. This creates two mismatches:

  1. Encoded semicolons (`%3B`): Since `%3B` is not decoded by normalizedPath(), the matrix parameter stripping in
  pathWithoutMatrixParams() never sees it. The encoded semicolon and everything after it become part of the path
  segment, causing policy matching to fail. This affects all path-policy-protected endpoints.
  2. Static resource path mismatch: Static resource handlers (StaticHandlerImpl, FileSystemStaticHandler) perform full
  percent-decoding via URIDecoder.decodeURIComponent() and backslash-to-slash conversion before filesystem resolution.
  Reserved characters like `%2F` (slash) and `%5C` (backslash) that survive the security layer's partial decoding are fully
  decoded before file serving.

  REST endpoints using Quarkus REST (RESTEasy Reactive) are not affected by the `%2F/%5C` vectors because the routing layer also uses `normalizedPath()` — both security and routing agree on the path, so no mismatch exists.

###  Attack Vectors

  Encoded semicolon (matrix parameter smuggling), affects all path-policy-protected endpoints:
  
  - `/api/admin%3Bbypass=true/data`: security sees this as a single segment `admin%3Bbypass=true`, which does not match the
   `/api/admin/* policy`. The request passes through unauthenticated.
  - `/api/secret%3b/data`: same mechanism with lowercase hex digit.

  Encoded slash/backslash on static resources, affects static files behind path policies:
  - `/static-secret%2Fhtml`, security does not match /static-secret.html policy; static handler decodes `%2F` to `/` and may
  resolve the file.
  - `/static-secret%5Chtml `. static handler decodes `%5C` to `\`, then converts to `/`.

  Double encoding, affects static resources:
  - `/secret%252Fconfidential.html`, first decode by normalizedPath() turns `%25` into `%`, producing `%2F`. Static handler's
  second decode turns `%2F` into `/`.

  The following vectors were investigated and confirmed not exploitable:

  - Unreserved character encoding (`/api/adm%69n/data`): `normalizedPath()` decodes these. Both security and routing see
  `/api/admin/data`. 
  - Null byte injection (`/api/admin%00/data`): `%00` is not decoded by `normalizedPath()`. 
  - Encoded dot segments (`/api/%2e%2e/secret/data`): Period is unreserved, so `%2e` is decoded to `.` by `normalizedPath()`,
  then `removeDots()` normalizes `..` segments. 
  - REST endpoint bypass via `%2F/%5C`: Routing uses the same `normalizedPath()` as security. The encoded slash/backslash
  doesn't match any route. 

###   Root Cause

  `pathWithoutMatrixParams()` operates on the partially-decoded output of `normalizedPath()`, where reserved characters
  remain encoded. It searches for literal ; but never sees `%3B.` The fix (`normalizePath()`) performs full percent-decoding
   in a loop before stripping matrix parameters, removing null bytes, normalizing backslashes, and resolving dot
  segments, aligning the security layer's view of the path with what downstream handlers resolve.

###  Impact

  - Unauthenticated access to endpoints protected by `quarkus.http.auth.permission` path-based policies via `%3B` smuggling
  - Static resource exposure by bypassing path policies on protected files via `%2F/%5C`
  - Applications using annotation-based security (`@RolesAllowed`, `@Authenticated`) on JAX-RS resources without path-based
  policies are not affected by the `%2F/%5C` vectors, but may still be affected by `%3B` if path policies coexist

###  Proof of Concept

```
  # Encoded semicolon bypass — works on any path-policy-protected endpoint
  # Security sees "/api/admin%3Bbypass=true/data", doesn't match /api/admin/* policy
  curl -v http://target/api/admin%3Bbypass=true/data

  # Encoded semicolon on authenticated endpoint
  curl -v http://target/api/secret%3b/data

  # Static resource bypass via encoded slash (if static file behind path policy)
  curl -v http://target/static-secret%2Fhtml

  # Static resource bypass via encoded backslash
  curl -v http://target/static-secret%5Chtml
```

## References
- https://github.com/quarkusio/quarkus/security/advisories/GHSA-qcxp-gm7m-4j5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-50559
- https://github.com/quarkusio/quarkus/commit/919b80017d85564143a845b38e9cca54aff5b3cc
- https://access.redhat.com/errata/RHSA-2026:26017
- https://access.redhat.com/errata/RHSA-2026:26018
- https://access.redhat.com/errata/RHSA-2026:26194
- https://access.redhat.com/errata/RHSA-2026:26586
- https://access.redhat.com/errata/RHSA-2026:34608
- https://access.redhat.com/errata/RHSA-2026:36820
- https://access.redhat.com/errata/RHSA-2026:48151
- https://access.redhat.com/security/cve/CVE-2026-50559
- https://bugzilla.redhat.com/show_bug.cgi?id=2486959
- https://github.com/quarkusio/quarkus
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-50559.json
