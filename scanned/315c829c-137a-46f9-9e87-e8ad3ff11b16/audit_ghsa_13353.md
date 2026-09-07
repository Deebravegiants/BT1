# [H] Paths contain matrix variables bypass decorators

## Summary
Severity: High
Advisory: GHSA-wvp2-9ppw-337j
CVE: CVE-2023-38493
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-wvp2-9ppw-337j
Type: github-advisory

## Affected
- Maven: `com.linecorp.armeria:armeria` — affected >=0 <1.24.3

## Details
### Impact
Spring supports [Matrix variables](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/matrix-variables.html).
When Spring integration is used, Armeria calls Spring controllers via `TomcatService` or `JettyService` with the path
that may contain matrix variables.
In this situation, the Armeria decorators might not invoked because of the matrix variables.
Let's see the following example:
```
// Spring controller
@GetMapping("/important/resources")
public String important() {...}

// Armeria decorator
ServerBuilder sb = ...
sb.decoratorUnder("/important/", authService);
```
If an attacker sends a request with `/important;a=b/resources`, the request would bypass the authrorizer

### Patches
- https://github.com/line/armeria-ghsa-wvp2-9ppw-337j/commit/9b0ec3e099cc05fbff11d7f1012a1dddb0000d0c

### Workarounds
Users can add decorators using regex. `e.g. "regex:^/important.*"`

## References
- https://github.com/line/armeria/security/advisories/GHSA-wvp2-9ppw-337j
- https://nvd.nist.gov/vuln/detail/CVE-2023-38493
- https://github.com/line/armeria/commit/039db50bbfc88014ea8737fd1e1ddd6fd3fc4f07
- https://github.com/line/armeria/commit/49e04ef231ad65750739529c7fa4ce946ff7588b
- https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/matrix-variables.html
- https://github.com/line/armeria
