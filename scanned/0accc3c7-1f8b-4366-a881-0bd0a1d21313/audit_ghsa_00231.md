# [H] Path Traversal in superstatic

## Summary
Severity: High
Advisory: GHSA-wm77-q74p-5763
CWE: CWE-177
Ecosystem: npm
Published: 2018-07-27
Source: https://github.com/advisories/GHSA-wm77-q74p-5763
Type: github-advisory

## Affected
- npm: `superstatic` — affected >=0 <5.0.2

## Details
Affected of `superstatic` are vulnerable to path traversal when used on Windows. 

Additionally, it is vulnerable to path traversal on other platforms combined with certain Node.js versions which erroneously normalize `\\` to `/` in paths on all platforms (a known example being Node.js v9.9.0).


## Recommendation

Update to version 5.0.2 or later.

## References
- https://github.com/firebase/superstatic/pull/255
- https://github.com/firebase/superstatic/commit/e396ff62f588732989137d6c40d46b310e51ef2b
- https://github.com/firebase/superstatic/blob/v5.0.1/lib/providers/fs.js#L71
- https://www.npmjs.com/advisories/652
