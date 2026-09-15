# [H] Improper Handling of Unexpected Data Type in ced

## Summary
Severity: High
Advisory: GHSA-27wq-qx3q-fxm9
CVE: CVE-2021-39131
CWE: CWE-241
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-27wq-qx3q-fxm9
Type: github-advisory

## Affected
- npm: `ced` — affected >=0 <1.0.0

## Details
### Impact

In ced v0.1.0, passing data types other than `Buffer` causes the Node.js process to crash.

### Patches

The problem has been patched in [ced v1.0.0](https://github.com/sonicdoe/ced/releases/tag/v1.0.0). You can upgrade from v0.1.0 without any breaking changes.

### Workarounds

Before passing an argument to ced, verify it’s a `Buffer` using [`Buffer.isBuffer(obj)`](https://nodejs.org/api/buffer.html#buffer_static_method_buffer_isbuffer_obj).

### CVSS score

[CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/RL:O/RC:C](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/RL:O/RC:C)

Base Score: 7.5 (High)
Temporal Score: 7.2 (High)

Since ced is a library, the scoring is based on the “[reasonable worst-case implementation scenario](https://www.first.org/cvss/v3.1/user-guide#3-7-Scoring-Vulnerabilities-in-Software-Libraries-and-Similar)”, namely, accepting data from untrusted sources over a network and passing it directly to ced. Depending on your specific implementation, the vulnerability’s severity in your program may be different.

### Proof of concept

```js
const express = require("express");
const bodyParser = require("body-parser");
const ced = require("ced");

const app = express();

app.use(bodyParser.raw());

app.post("/", (req, res) => {
  const encoding = ced(req.body);

  res.end(encoding);
});

app.listen(3000);
```

`curl --request POST --header "Content-Type: text/plain" --data foo http://localhost:3000` crashes the server.

### References

- https://github.com/sonicdoe/ced/commit/a4d9f10b6bf1cd468d1a5b9a283cdf437f8bb7b3

## References
- https://github.com/sonicdoe/ced/security/advisories/GHSA-27wq-qx3q-fxm9
- https://nvd.nist.gov/vuln/detail/CVE-2021-39131
- https://github.com/sonicdoe/ced/commit/a4d9f10b6bf1cd468d1a5b9a283cdf437f8bb7b3
- https://github.com/sonicdoe/ced
- https://github.com/sonicdoe/ced/releases/tag/v1.0.0
