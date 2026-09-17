# [M] Eclipse Jetty: HTTP Authority/Host mismatch

## Summary
Severity: Medium
Advisory: GHSA-7p3p-8qv8-m2vh
CVE: CVE-2026-6790
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-7p3p-8qv8-m2vh
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0.v20161208
- Maven: `org.eclipse.jetty:jetty-server` — affected >=10.0.0
- Maven: `org.eclipse.jetty:jetty-server` — affected >=11.0.0
- Maven: `org.eclipse.jetty:jetty-server` — affected >=12.0.0 <12.0.35
- Maven: `org.eclipse.jetty:jetty-server` — affected >=12.1.0 <12.1.9

## Details
#### Summary

Jetty currently accepts HTTP/2 and HTTP/3 requests where the regular
Host header and the pseudo-header :authority
do not match. As a result, the same request can carry two different host identities
through Jetty:

- logic based on `HttpURI` / `Request.getServerName(request)` uses `:authority`
- logic based on raw request headers continues to use `Host`

This creates a host/authority confusion condition that can break
security assumptions in higher layers.

Jetty already performs an explicit authority/Host consistency check on
the HTTP/1.1 path, but equivalent validation is missing on the HTTP/2
and HTTP/3 paths.

#### Security Impact

This issue is not inherently remote code execution, but it can become
security-relevant in deployments that rely on the request host for
security-sensitive decisions, including:

- host-based access control
- virtual host isolation
- multi-tenant routing by hostname
- login/logout/callback URL construction
- reverse proxy and forwarded-header trust chains
- auditing, cache keys, and absolute URL generation

Potential consequences include:

- bypass of host-based ACLs
- virtual host or tenant isolation failures
- incorrect or attacker-influenced redirect/callback targets
- inconsistent proxy/downstream interpretation of the original target host
- misleading logs and audit records

#### Technical Root Cause

1. On the HTTP/2 and HTTP/3 metadata builder paths:

- `:authority` is parsed separately into authority/URI state
- `Host` is preserved as a normal request header
- the two values are not compared for consistency

2. On the HTTP/2 and HTTP/3 server entry paths:

- Jetty calls `ComplianceUtils.verify(httpCompliance, requestMetaData, listener)`
- this verification does not enforce `MISMATCHED_AUTHORITY`

3. On the HTTP/1.1 path:

- Jetty explicitly checks whether authority and `Host` match
- mismatches are rejected by default

#### Relevant Code Locations

HTTP/2 metadata builder:

- `jetty-core/jetty-http2/jetty-http2-hpack/src/main/java/org/eclipse/jetty/http2/hpack/internal/MetaDataBuilder.java`

HTTP/3 metadata builder:

- `jetty-core/jetty-http3/jetty-http3-qpack/src/main/java/org/eclipse/jetty/http3/qpack/internal/metadata/MetaDataBuilder.java`

HTTP/2 server entry:

- `jetty-core/jetty-http2/jetty-http2-server/src/main/java/org/eclipse/jetty/http2/server/internal/HttpStreamOverHTTP2.java`

HTTP/3 server entry:

- `jetty-core/jetty-http3/jetty-http3-server/src/main/java/org/eclipse/jetty/http3/server/internal/HttpStreamOverHTTP3.java`

Shared HTTP compliance verification:

- `jetty-core/jetty-http/src/main/java/org/eclipse/jetty/http/ComplianceUtils.java`

HTTP/1.1 authority/Host consistency check:

- `jetty-core/jetty-server/src/main/java/org/eclipse/jetty/server/internal/HttpConnection.java`

Defined but not enforced on H2/H3:

- `jetty-core/jetty-http/src/main/java/org/eclipse/jetty/http/HttpCompliance.java`
- violation: MISMATCHED_AUTHORITY

#### Reproduction

I reproduced this on local Jetty 12.1.9-SNAPSHOT source.

Minimal reproduction steps:

1. Start a Jetty HTTP/2 or HTTP/3 test server.
2. Send a request with:
    - :authority = localhost:<port>
    - Host = evil.example:<port>
3. In the request handler, inspect both:
    - Request.getServerName(request)
    - request.getHeaders().get(HttpHeader.HOST)
4. Observe whether Jetty rejects the request or allows both values to remain visible.
Observed result:
    - HTTP/2: request is accepted and returns 200
    - HTTP/3: request is accepted and returns 200
    - the server can observe both:
        - serverName=localhost
        - hostHeader=evil.example:<port>

This shows that a single attacker-controlled request can preserve two conflicting host interpretations inside Jetty.

#### Tests Used


HTTP/2 rejection test:

- `org.eclipse.jetty.http2.tests.HTTP2Test#testRejectMismatchedHostHeaderAndAuthority`

HTTP/2 exploitability test:

- `org.eclipse.jetty.http2.tests.HTTP2Test#testMismatchedHostHeaderAndAuthoritySplitsAuthorityFromHostHeader`

HTTP/3 rejection test:

- `org.eclipse.jetty.http3.tests.HandlerClientServerTest#testRejectMismatchedHostHeaderAndAuthority`

HTTP/3 exploitability test:

- `org.eclipse.jetty.http3.tests.HandlerClientServerTest#testMismatchedHostHeaderAndAuthoritySplitsAuthorityFromHostHeader`


Observed behavior:

- both rejection tests fail because Jetty returns 200 instead of 400
- both exploitability tests pass, confirming that Jetty exposes different host values to different layers

#### Project-Internal Evidence of Real Impact

Examples:

- `jetty-openid` uses `Request.getServerName(request)` to construct redirect URLs
- `jetty-ee11-proxy` uses the raw `Host` header when building `Forwarded`

This indicates that the issue is not merely theoretical: Jetty’s own
ecosystem already contains code paths where different host sources are
used for different purposes.

#### Affected Version

Confirmed affected version:

- 12.1.9-SNAPSHOT

Other versions may also be affected if they share the same HTTP/2 /
HTTP/3 request construction and compliance-validation logic. I have
not yet completed a historical version matrix and would recommend
confirming exact affected ranges from Jetty’s branch history.


#### Suggested Fix

Recommend adding HTTP/2 and HTTP/3 validation equivalent to the
existing HTTP/1.1 authority/Host consistency check:

- if both :authority and regular Host are present
    - normalize and compare them
    - if they do not match, reject the request with 400 Bad Request
    - route the failure through the existing MISMATCHED_AUTHORITY compliance mechanism

Also adding explicit HTTP/2 and HTTP/3 regression coverage for this case.

#### Disclosure Status

- not publicly disclosed
- no public issue filed
- shared only privately with the Jetty security contacts

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-7p3p-8qv8-m2vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-6790
- https://github.com/jetty/jetty.project/issues/14870
- https://github.com/jetty/jetty.project/pull/14871
- https://github.com/jetty/jetty.project/pull/14897
- https://github.com/jetty/jetty.project/pull/14970
- https://github.com/jetty/jetty.project/commit/3e5a4daec196859b8886b6f67b1157dab47cdb6f
- https://github.com/jetty/jetty.project/commit/67ba9e6b39661810123680d9c894e99a7940c73d
- https://github.com/jetty/jetty.project/commit/cbca3076f7c914a232e7a8b22fa95fbf7e67a6cc
- https://github.com/jetty/jetty.project
- https://github.com/jetty/jetty.project/releases/tag/jetty-12.0.35
- https://github.com/jetty/jetty.project/releases/tag/jetty-12.1.9
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/99
