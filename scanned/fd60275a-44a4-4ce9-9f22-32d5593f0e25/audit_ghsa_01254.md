# [H] Byass due to validation before canonicalization in serve

## Summary
Severity: High
Advisory: GHSA-wm7q-rxch-43mx
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-wm7q-rxch-43mx
Type: github-advisory

## Affected
- npm: `serve` — affected >=0 <6.5.2

## Details
Versions of `serve` before 6.5.2 are vulnerable to the bypass of the ignore functionality. The bypass is possible because validation happens before canonicalization of paths and filenames.



Example:
Here we have a server that ignores the file test.txt.
```
const serve = require('serve')
const server = serve(__dirname, {
      port: 1337,
      ignore: ['test.txt']
})
```

Using the URL encoded form of a letter (%65 instead of e) attacker can bypass the ignore control accessing the file. 

`curl http://localhost:1337/t%65st.txt`

Additionally this technique can be used to get directory listings of ignored directories.


## Recommendation

Update to version 6.5.2 or later.

## References
- https://hackerone.com/reports/308721
- https://www.npmjs.com/advisories/594
