# [C] Unauthenticated RCE in Taskcluster web-server via GraphQL filter argument (sift $where)

## Summary
Severity: Critical
Program: Mozilla
Weakness: Code Injection
Reporter: griffinf
State: resolved
Disclosed: 2026-08-05T15:50:21.517Z
Source: https://hackerone.com/reports/3782701

## Details
## Summary

The public GraphQL endpoint at `/graphql` allows an unauthenticated caller to execute arbitrary JavaScript inside the web-server's Node.js process. The query argument `filter` is a free-form JSON object that the server passes directly into the `sift` library. The version in use (`sift` 17.1.3) compiles a `$where` string into a function using `new Function` and executes it.

Code execution has been confirmed, including the ability to run shell commands as the `node` user and read the full process environment. That environment contains PostgreSQL credentials, the Taskcluster deployment access token, Auth0 and GitHub OAuth client secrets, Pulse credentials, and database column-encryption keys. Exploiting this endpoint effectively compromises the entire instance, including the one running Firefox CI.

No authentication, token, or special headers are required. This can be exploited with a single POST request.

## Technical Details

### Root Cause Chain

**1. The filter goes straight into sift.** From `services/web-server/src/utils/sift.js`:

```js
import sift from 'sift';
export default (filter, array) => {
  if (!array) return [];
  return filter ? array.filter(sift(filter)) : array;
};
```

Whatever JSON the client sends as `filter` becomes `sift(filter)` with the default operator set. Nothing is stripped or validated.

**2. sift turns a `$where` string into code.** From `sift` 17.1.3:

```js
const $where = (params, ownerQuery, options) => {
  let test;
  if (isFunction(params)) {
    test = params;
  } else if (!process.env.CSP_ENABLED) {
    test = new Function("obj", "return " + params);   // <-- string becomes code
  } else {
    throw new Error(`In CSP mode, sift does not support strings in "$where" condition`);
  }
  return new EqualsOperation((b) => test.bind(b)(b), ownerQuery, options);
};
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3782701_
