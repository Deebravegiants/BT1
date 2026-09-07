# [M] @octokit/request-error has a Regular Expression in index that Leads to ReDoS Vulnerability Due to Catastrophic Backtracking

## Summary
Severity: Medium
Advisory: GHSA-xx4v-prfh-6cgc
CVE: CVE-2025-25289
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-xx4v-prfh-6cgc
Type: github-advisory

## Affected
- npm: `@octokit/request-error` — affected >=1.0.0 <5.1.1
- npm: `@octokit/request-error` — affected >=6.0.0 <6.1.7

## Details
### Summary
A Regular Expression Denial of Service (ReDoS) vulnerability exists in the processing of HTTP request headers. By sending an authorization header containing an excessively long sequence of spaces followed by a newline and "@", an attacker can exploit inefficient regular expression processing, leading to excessive resource consumption. This can significantly degrade server performance or cause a denial-of-service (DoS) condition, impacting availability.
### Details
The issue occurs at [line 52](https://github.com/octokit/request-error.js/blob/main/src/index.ts) of iterator.ts in the @octokit/request-error repository.
The vulnerability is caused by the use of an inefficient regular expression in the handling of the `authorization` header within the request processing logic:
```js
authorization: options.request.headers.authorization.replace(
  / .*$/, 
  " [REDACTED]"
)
```
The regular expression `/ .*$/` matches a space followed by any number of characters until the end of the line. This pattern is vulnerable to Regular Expression Denial of Service (ReDoS) when processing specially crafted input. Specifically, an attacker can send an `authorization` header containing a long sequence of spaces followed by a newline and "@", such as:
```js
headers: {
  authorization: "" + " ".repeat(100000) + "\n@",
}
```
Due to the way JavaScript's regular expression engine backtracks while attempting to match the space followed by arbitrary characters, this input can cause excessive CPU usage, significantly slowing down or even freezing the server. This leads to a denial-of-service condition, impacting availability.
### PoC
[The gist of PoC.js](https://gist.github.com/ShiyuBanzhou/e1203ad22701fd043b8501eb37676a0d)
1. run npm i @octokit/request-error
2. run 'node poc.js'
result:
3. then the program will stuck forever with high CPU usage
```js
import { RequestError } from "@octokit/request-error";

const error = new RequestError("Oops", 500, {
  request: {
    method: "POST",
    url: "https://api.github.com/foo",
    body: {
      bar: "baz",
    },
    headers: {
      authorization: ""+" ".repeat(100000)+"\n@",
    },
  },
  response: {
    status: 500,
    url: "https://api.github.com/foo",
    headers: {
      "x-github-request-id": "1:2:3:4",
    },
    data: {
      foo: "bar",
    },
  },
});
```

### Impact
#### Vulnerability Type & Impact:
This is a `Regular Expression Denial of Service (ReDoS) vulnerability`, which occurs due to an inefficient regular expression (`/ .*$/`) used to sanitize the `authorization` header. An attacker can craft a malicious input that triggers excessive backtracking in the regex engine, leading to high CPU consumption and potential denial-of-service (DoS).
#### Who is Impacted?
* Projects or services using this code to process HTTP headers are vulnerable.
* Applications that rely on user-supplied `authorization` headers are at risk, especially those processing a large volume of authentication requests.
* Multi-tenant or API-driven platforms could experience degraded performance or service outages if exploited at scale.

## References
- https://github.com/octokit/request-error.js/security/advisories/GHSA-xx4v-prfh-6cgc
- https://nvd.nist.gov/vuln/detail/CVE-2025-25289
- https://github.com/octokit/request-error.js/commit/d558320874a4bc8d356babf1079e6f0056a59b9e
- https://github.com/octokit/request-error.js
- https://github.com/octokit/request-error.js/blob/main/src/index.ts
