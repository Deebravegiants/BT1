# [H] Path Traversal in com.linecorp.armeria:armeria

## Summary
Severity: High
Advisory: GHSA-8fp4-rp6c-5gcv
CVE: CVE-2021-43795
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-02
Source: https://github.com/advisories/GHSA-8fp4-rp6c-5gcv
Type: github-advisory

## Affected
- Maven: `com.linecorp.armeria:armeria` — affected >=1.12.0 <1.13.4

## Details
### Impact

An attacker can access an Armeria server's local file system beyond its restricted directory by sending an HTTP request whose path contains `%2F` (encoded `/`), such as `/files/..%2Fsecrets.txt`, bypassing Armeria's path validation logic.

### Patches

Armeria 1.13.4 or above contains the hardened path validation logic that handles `%2F` properly. 

### Workarounds

This vulnerability can be worked around by inserting a decorator that performs an additional validation on the request path, e.g.

```java
Server
  .builder()
  .serviceUnder(
    "/files",
    FileService
      .of(...)
      .decorate((delegate, ctx, req) -> {
        String path = req.headers().path();
        if (path.contains("%2f") || path.contains("%2F")) {
          return HttpResponse.of(HttpStatus.BAD_REQUEST);
        }
        return delegate.serve(ctx, req);
      })
  )
  .build()
```

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [line/armeria](https://github.com/line/armeria)
* Chat with us at [Slack](https://armeria.dev/s/slack)

### Credits

This vulnerability was originally reported by Abdallah Zaher ([elcayser-0x0a](https://hackerone.com/elcayser-0x0a?type=user)).

## References
- https://github.com/line/armeria/security/advisories/GHSA-8fp4-rp6c-5gcv
- https://nvd.nist.gov/vuln/detail/CVE-2021-43795
- https://github.com/line/armeria/pull/3855
- https://github.com/line/armeria/commit/e2697a575e9df6692b423e02d731f293c1313284
- https://github.com/line/armeria
