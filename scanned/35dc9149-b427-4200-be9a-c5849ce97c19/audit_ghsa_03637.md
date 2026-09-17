# [M] Memory Exposure in tunnel-agent

## Summary
Severity: Medium
Advisory: GHSA-xc7v-wxcw-j472
CWE: CWE-200
Ecosystem: npm
Published: 2019-06-03
Source: https://github.com/advisories/GHSA-xc7v-wxcw-j472
Type: github-advisory

## Affected
- npm: `tunnel-agent` — affected >=0 <0.6.0

## Details
Versions of `tunnel-agent` before 0.6.0 are vulnerable to memory exposure.

This is exploitable if user supplied input is provided to the auth value and is a number.

Proof-of-concept:
```js
require('request')({
  method: 'GET',
  uri: 'http://www.example.com',
  tunnel: true,
  proxy:{
    protocol: 'http:',
    host:'127.0.0.1',
    port:8080,
    auth:USERSUPPLIEDINPUT // number
  }
});
```


## Recommendation

Update to version 0.6.0 or later.

## References
- https://github.com/request/tunnel-agent/commit/9ca95ec7219daface8a6fc2674000653de0922c0
- https://gist.github.com/ChALkeR/fd6b2c445834244e7d440a043f9d2ff4
- https://www.npmjs.com/advisories/598
