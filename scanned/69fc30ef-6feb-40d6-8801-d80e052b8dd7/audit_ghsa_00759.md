# [M] Default development error handler in Ratpack is vulnerable to HTML content injection (XSS)

## Summary
Severity: Medium
Advisory: GHSA-r2wf-q3x4-hrv9
CVE: CVE-2019-10770
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-01-27
Source: https://github.com/advisories/GHSA-r2wf-q3x4-hrv9
Type: github-advisory

## Affected
- Maven: `io.ratpack:ratpack-core` — affected >=0 <1.7.6

## Details
Versions of Ratpack from 0.9.10 through 1.7.5 are vulnerable to [CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')](https://cwe.mitre.org/data/definitions/79.html) (aka. XSS) in the development error handler. An attacker can utilize this to perform XSS when an exception message contains untrusted data.

As a simplistic example:
```java
RatpackServer startedServer = RatpackServer.start(server -> {
    server.handlers(chain -> chain.all(ctx -> {
        // User supplied query parameter
        String message = ctx.getRequest().getQueryParams().get("message");
        // User supplied data appended to the message in an exception
        throw new RuntimeException("An error occurred: " + message);
    }));
});
```

### Impact

 - Cross-Site Scripting

### Patches

This vulnerability has been patched in Ratpack version 1.7.6.

### Workarounds

If you are unable to update your version of Ratpack, we recommend the following workarounds and mitigations.

 - Ensure that development mode is disabled in production.
 - Don't use real customer data (ie. untrusted user input) in development.

### References

 - [Ratpack development mode](https://ratpack.io/manual/current/api/ratpack/server/ServerConfigBuilder.html#development-boolean-)
 - [Code Patch - a3cbb13](https://github.com/ratpack/ratpack/commit/a3cbb13be1527874528c3b99fc33517c0297b6d3)

### For more information

If you have any questions or comments about this advisory:
 - Open an issue in [ratpack/ratpack](https://github.com/ratpack/ratpack/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)
 - Ask in our [Slack channel](https://slack-signup.ratpack.io/)

## References
- https://github.com/ratpack/ratpack/security/advisories/GHSA-r2wf-q3x4-hrv9
- https://nvd.nist.gov/vuln/detail/CVE-2019-10770
- https://github.com/ratpack/ratpack/commit/a3cbb13be1527874528c3b99fc33517c0297b6d3
- https://snyk.io/vuln/SNYK-JAVA-IORATPACK-534882
