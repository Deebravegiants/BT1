# [H] CVE-2018-7158

## Summary
Severity: High
Advisory: CVE-2018-7158
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-17
Source: https://osv.dev/vulnerability/CVE-2018-7158
Type: osv

## Details
The `'path'` module in the Node.js 4.x release line contains a potential regular expression denial of service (ReDoS) vector. The code in question was replaced in Node.js 6.x and later so this vulnerability only impacts all versions of Node.js 4.x. The regular expression, `splitPathRe`, used within the `'path'` module for the various path parsing functions, including `path.dirname()`, `path.extname()` and `path.parse()` was structured in such a way as to allow an attacker to craft a string, that when passed through one of these functions, could take a significant amount of time to evaluate, potentially leading to a full denial of service.

## References
- https://nodejs.org/en/blog/vulnerability/march-2018-security-releases/
