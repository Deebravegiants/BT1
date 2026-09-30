# [M] @octokit/endpoint has a Regular Expression in parse that Leads to ReDoS Vulnerability Due to Catastrophic Backtracking

## Summary
Severity: Medium
Advisory: GHSA-x4c5-c7rf-jjgv
CVE: CVE-2025-25285
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-x4c5-c7rf-jjgv
Type: github-advisory

## Affected
- npm: `@octokit/endpoint` — affected >=9.0.5 <9.0.6
- npm: `@octokit/endpoint` — affected >=10.0.0 <10.1.3

## Details
### Summary
By crafting specific `options` parameters, the `endpoint.parse(options)` call can be triggered, leading to a regular expression denial-of-service (ReDoS) attack. This causes the program to hang and results in high CPU utilization.

### Details
The issue occurs in the `parse` function within the `parse.ts` file of the npm package `@octokit/endpoint`. The specific code is located at the following link: https://github.com/octokit/endpoint.js/blob/main/src/parse.ts, at line 62:
```ts
headers.accept.match(/[\w-]+(?=-preview)/g) || ([] as string[]);
```
The regular expression `/[\w-]+(?=-preview)/g` encounters a backtracking issue when it processes `a large number of characters` followed by the `-` symbol.
e.g., the attack string: 
```js
"" + "A".repeat(100000) + "-"
```

### PoC
[The gist](https://gist.github.com/ShiyuBanzhou/a17202ac1ad403a80ca302466d5e56c4)
Here is the reproduction process for the vulnerability:
1. run `npm i @octokit/endpoint`
2. Move `poc.js` to the root directory of the same level as `README.md`
3. run `node poc.js`
result:
4. then the program will be stuck forever with high CPU usage
```js
import { endpoint } from "@octokit/endpoint";
// import { parse } from "./node_modules/@octokit/endpoint/dist-src/parse.js";
const options = {  
  method: "POST",
  url: "/graphql", // Ensure that the URL ends with "/graphql"
  headers: {
    accept: "" + "A".repeat(100000) + "-", // Pass in the attack string
    "content-type": "text/plain",
  },
  mediaType: {
    previews: ["test-preview"], // Ensure that mediaType.previews exists and has values
    format: "raw", // Optional media format
  },
  baseUrl: "https://api.github.com",
};

const startTime = performance.now();
endpoint.parse(options);
const endTime = performance.now();
const duration = endTime - startTime;
console.log(`Endpoint execution time: ${duration} ms`);
```
1. **Import the `endpoint` module**: First, import the `endpoint` module from the npm package `@octokit/endpoint`, which is used for handling GitHub API requests.

2. **Construct the `options` object that triggers a ReDoS attack**: The following member variables are critical in constructing the `options` object:
- `url`: Set to `"/graphql"`, ensuring the URL ends with `/graphql` to match the format for GitHub's GraphQL API.
- `headers`:
> `accept`: A long attack string is crafted with `"A".repeat(100000) + "-"`, which will be passed to the regular expression and cause a backtracking attack (ReDoS).
> 
- `mediaType`:
>`previews`: Set to `["test-preview"]`, ensuring `mediaType.previews` exists and has values.
>
>`format`: Set to `"raw"`, indicating raw data format.

3. **Call the `endpoint.parse(options)` function and record the time**: Call the `endpoint.parse(options)` function and use `performance.now()` to record the start and end times, measuring the execution duration.

4. **Calculate the time difference and output it**: Compute the difference between the start and end times and output it using `console.log`. When the attack string length reaches 100000, the response time typically exceeds 10000 milliseconds, satisfying the characteristic condition for a ReDoS attack, where response times dramatically increase.
<img width="800" alt="2" src="https://github.com/user-attachments/assets/9fc865a4-e150-42d5-bcd5-93ab6b0c29ef" />

### Impact
#### What kind of vulnerability is it?
This is a **Regular Expression Denial of Service (ReDoS)** vulnerability. It arises from inefficient regular expressions that can cause excessive backtracking when processing certain inputs. Specifically, the regular expression `/[\w-]+(?=-preview)/g` is vulnerable because it attempts to match long strings of characters followed by a hyphen (`-`), which leads to inefficient backtracking when provided with specially crafted attack strings. This backtracking results in high CPU utilization, causing the application to become unresponsive and denying service to legitimate users.
#### Who is impacted?
This vulnerability impacts any application that uses the affected regular expression in conjunction with user-controlled inputs, particularly where large or maliciously crafted strings can trigger excessive backtracking.
In addition to directly affecting applications using the `@octokit/endpoint` package, the impact is more widespread because `@octokit/endpoint` is a library used to wrap REST APIs, including GitHub's API. This means that any system or service built on top of this library that interacts with GitHub or other REST APIs could be vulnerable. Given the extensive use of this package in API communication, the potential for exploitation is broad and serious. The vulnerability could affect a wide range of applications, from small integrations to large enterprise-level systems, especially those relying on the package to handle API requests.
Attackers can exploit this vulnerability to cause performance degradation, downtime, and service disruption, making it a critical issue for anyone using the affected version of `@octokit/endpoint`.

### Solution
To resolve the ReDoS vulnerability, the regular expression should be updated to avoid excessive backtracking. By modifying the regular expression to `(?<![\w-])[\w-]+(?=-preview)`, we prevent the issue.
Here is how this change solves the problem:

1. **Old Regular Expression**: `/[\w-]+(?=-preview)/g`
- This regular expression matches any sequence of word characters (`\w`) and hyphens (`-`) followed by `-preview`.
- The issue arises when the regex engine encounters a long string of characters followed by a `-`, causing excessive backtracking and high CPU usage.
2. **New Regular Expression**: `(?<![\w-])[\w-]+(?=-preview)`
- This updated regular expression uses a negative lookbehind `(?<![\w-])`, ensuring that the matched string is not preceded by any word characters or hyphens (`\w` or `-`).
- The new expression still matches sequences of word characters and hyphens, but the negative lookbehind ensures it doesn't cause backtracking issues when processing long attack strings.
- By adding this lookbehind, we effectively prevent the vulnerability, ensuring the regex operates efficiently without excessive backtracking.

#### Full Solution Example:
The specific code is located at the following link: https://github.com/octokit/endpoint.js/blob/main/src/parse.ts, at line 62:
1. **Update the Regular Expression**: In the `parse.ts` file (or wherever the original regex is defined), replace the existing regular expression:
```ts
const previewsFromAcceptHeader =
          headers.accept.match(/[\w-]+(?=-preview)/g) || ([] as string[]);
```
With the updated one:
```ts
const previewsFromAcceptHeader =
          headers.accept.match(/(?<![\w-])[\w-]+(?=-preview)/g) || ([] as string[]);
```

2. **Test the Change**: After updating the regular expression, thoroughly test the application with both regular and malicious inputs to ensure that:
- The functionality remains correct and the expected matches still occur.
- The performance improves and the ReDoS vulnerability no longer occurs when handling large attack strings.
3. **Deploy the Fix**: Once the solution is verified, deploy the fix to your production environment to protect against potential attacks.

## References
- https://github.com/octokit/endpoint.js/security/advisories/GHSA-x4c5-c7rf-jjgv
- https://nvd.nist.gov/vuln/detail/CVE-2025-25285
- https://github.com/octokit/endpoint.js/commit/6c9c5be033c450d436efb37de41b6470c22f7db8
- https://github.com/octokit/endpoint.js
- https://github.com/octokit/endpoint.js/blob/main/src/parse.ts
