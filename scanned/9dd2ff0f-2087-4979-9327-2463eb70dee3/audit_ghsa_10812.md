# [M] Apollo Router Core: Browser Bug Enables Bypass of XS-Search Prevention via Read-Only Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-hff2-gcpx-8f4p
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-hff2-gcpx-8f4p
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=2.11.0 <2.12.1
- crates.io: `apollo-router` — affected >=2.0.0 <2.10.2
- crates.io: `apollo-router` — affected >=0 <1.61.13

## Details
### Impact
In a Cross-Site Request Forgery attack, untrusted web content causes browsers to send authenticated requests to web servers which use cookies for authentication. While the web content is prevented from reading the request's response due to the Cross-Origin Request Sharing (CORS) protocol, the attacker may be able to cause side effects in the server ("CSRF" attack), or learn something about the response via timing analysis ("XS-Search" attack).

Apollo Router has a built-in feature which prevents CSRF and XS-Search attacks: it refuses to process GraphQL requests that could possibly have been sent by a spec-compliant web browser without a protective "preflight" step. See [Apollo Router's docs](https://www.apollographql.com/docs/graphos/routing/security/csrf) for more details on CORS, CSRF attacks, and Apollo Router's CSRF prevention feature.

This feature is fully effective against attacks carried out against users of spec-compliant browsers. Unfortunately, a major browser introduced a bug in 2025 which meant in certain cases, it failed to follow the CORS spec. The browser's maintainers have already committed to fixing the bug and making the browser spec-compliant again.

Even with this bug, Apollo Router's CSRF prevention feature **blocks** "side effect" CSRF attacks: Apollo Router will still correctly refuse to execute _mutations_ in requests that were not preflighted. However, some specially crafted authenticated GraphQL _queries_ can be issued across origins *without preflight* in buggy versions of this browser, allowing for XS-Search attacks: an attacker can analyze response times to learn facts about the responses to requests such as whether fields return null or approximately how many list entries are returned from fields.

Apollo Router installations are only vulnerable if they rely on cookies (or HTTP Basic Auth) for authentication.

### Patches
The vulnerability is patched in the following versions of Apollo Router:

- 2.12.1 (latest)
- 2.10.2 (v2.10 LTS)
- 1.61.13 (v1; note that Router v1 reaches [end-of-support on March 31 2026](https://www.apollographql.com/docs/graphos/resources/runtime-release-lifecycle#end-of-support-eos))

These releases contain a single change: GraphQL requests sent in HTTP `GET` requests which contain a `Content-Type` header naming a type other than `application/json` are rejected. (`GET` requests with no `Content-Type` are allowed.) This change prevents XS-Search attacks even in browsers which are non-compliant in ways similar to this browser.

There are no known cases where GraphQL apps depend on the ability of clients to send non-empty `Content-Type` headers with GET requests other than `application/json`, so this change has not been made configurable; if this change breaks a specific use case, contact support and more configurability can be added.

#### Workarounds
If upgrading is not possible, this particular browser's bug can be mitigated by preventing any HTTP request with a `Content-Type` header containing `message/` from reaching the Apollo Router (e.g. in a load balancer/proxy).

If the load balancer cannot easily be updated to block these requests, it can also be done with a Rhai script within Router:

```
# config.yaml
rhai:
  scripts: "/directory/with/rhai/script"
  main: "main.rhai"

# main.rhai
fn router_service(service) {
    const request_callback = Fn("process_request");
    service.map_request(request_callback);
}

fn process_request(request) {
    if "content-type" in request.headers {
        if request.headers["content-type"].contains("message/") {
            throw "Error: invalid content type"
        }
    }
}
```

While the patch prevents a broader class of similar issues, the only known way to exploit this vulnerability is against a particular browser which currently plans to ship a fix in May 2026. If it is already past June 2026 and this vulnerability has not been addressed yet, it is likely that the installation is not currently vulnerable. Upgrading to the latest version of Apollo Router is still recommended for the broader protection.

### Resources
The browser bug causes a similar vulnerability in Apollo Server; see https://github.com/apollographql/apollo-server/security/advisories/GHSA-9q82-xgwf-vj

## References
- https://github.com/apollographql/apollo-server/security/advisories/GHSA-9q82-xgwf-vj6h
- https://github.com/apollographql/router/security/advisories/GHSA-hff2-gcpx-8f4p
- https://github.com/apollographql/router/commit/a72e759bcdeef93fcd3dc928cf3c1f4bbebdcc65
- https://github.com/apollographql/router
- https://github.com/apollographql/router/releases/tag/v2.12.1
- https://www.apollographql.com/docs/graphos/resources/runtime-release-lifecycle#end-of-support-eos
