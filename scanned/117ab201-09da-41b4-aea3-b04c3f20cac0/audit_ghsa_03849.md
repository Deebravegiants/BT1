# [H] io.ratpack:ratpack-core vulnerable to Improper Neutralization of Special Elements in Output ('Injection')

## Summary
Severity: High
Advisory: GHSA-mvqp-q37c-wf9j
CVE: CVE-2019-17513
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-10-21
Source: https://github.com/advisories/GHSA-mvqp-q37c-wf9j
Type: github-advisory

## Affected
- Maven: `io.ratpack:ratpack-core` — affected >=0 <1.7.5

## Details
## CWE-113: Improper Neutralization of CRLF Sequences in HTTP Headers ('HTTP Response Splitting')

Versions of Ratpack 0.9.1 through and including 1.7.4 are vulnerable to [HTTP Response Splitting](https://www.owasp.org/index.php/HTTP_Response_Splitting), 
if untrusted and unsanitized data is used to populate the headers of an HTTP response.
An attacker can utilize this vulnerability to have the server issue any HTTP response they specify.

If your application uses arbitrary user input as the value of a response header it is vulnerable.
If your application does not use arbitrary values as response header values, it is not vulnerable.

Previously, Ratpack did not validate response header values.
Now, adding a header value that contains the header value termination characters (CRLF) produces a runtime exception.
Since there is no mechanism for escaping or encoding the termination characters in a String, a runtime exception is necessary.

As potentially dangerous values now cause runtime exceptions, it is a good idea to continue to validate and sanitize any user-supplied values being used as response headers.

We would like to thank [Jonathan Leitschuh](https://github.com/JLLeitschuh) for reporting this vulnerability.

### Vulnerable Example

The following example server uses a query parameter value as a response header, without validating or sanitizing it.
```java
RatpackServer startedServer =  RatpackServer.start(server -> {
    server.handlers(chain -> chain.all(ctx -> {
        // User supplied query parameter
        String header = ctx.getRequest().getQueryParams().get("header");
        // User supplied data used to populate a header value.
        ctx.header("the-header", header)
            .render("OK!");
    }));
});
```

Sending a request to the server with the following value for the `header` query param would allow the execution of arbitrary Javascript.

```
Content-Type: text/html
X-XSS-Protection: 0

<script>alert(document.domain)</script>
```

### Impact

- Cross-User Defacement
- Cache Poisoning
- Cross-Site Scripting
- Page Hijacking

### Patches

This vulnerability has been patched in Ratpack version 1.7.5.

### Root Cause

The root cause was due to using the netty `DefaultHttpHeaders` object with verification disabled.

https://github.com/ratpack/ratpack/blob/af1e8c8590f164d7dd84d4212886fad4ead99080/ratpack-core/src/main/java/ratpack/server/internal/NettyHandlerAdapter.java#L159

This vulnerability is now more clearly documented in the Netty documentation: https://github.com/netty/netty/pull/9646

### Workarounds

The workaround for this vulnerability is to either not use arbitrary input as response header values or validate such values before being used to ensure they don't contain a carriage return and/or line feed characters.

### References

 - [CWE-113: Improper Neutralization of CRLF Sequences in HTTP Headers ('HTTP Response Splitting')](https://cwe.mitre.org/data/definitions/113.html)
 - Fix commit: https://github.com/ratpack/ratpack/commit/efb910d38a96494256f36675ef0e5061097dd77d
 
### For more information

If you have any questions or comments about this advisory:
* Open an issue in [ratpack/ratpack](https://github.com/ratpack/ratpack/issues)
* Ask in our [Slack channel](https://slack-signup.ratpack.io/)

## References
- https://github.com/ratpack/ratpack/security/advisories/GHSA-mvqp-q37c-wf9j
- https://nvd.nist.gov/vuln/detail/CVE-2019-17513
- https://github.com/ratpack/ratpack/commit/c560a8d10cb8bdd7a526c1ca2e67c8f224ca23ae
- https://github.com/ratpack/ratpack/commit/efb910d38a96494256f36675ef0e5061097dd77d
- https://github.com/advisories/GHSA-mvqp-q37c-wf9j
- https://github.com/ratpack/ratpack
- https://github.com/ratpack/ratpack/releases/tag/v1.7.5
- https://ratpack.io/versions/1.7.5
