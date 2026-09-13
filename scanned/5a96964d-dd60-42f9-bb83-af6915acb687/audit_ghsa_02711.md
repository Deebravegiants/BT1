# [H] Missing Release of Memory after Effective Lifetime in detect-character-encoding

## Summary
Severity: High
Advisory: GHSA-5rwj-j5m3-3chj
CVE: CVE-2021-39176
CWE: CWE-401
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-5rwj-j5m3-3chj
Type: github-advisory

## Affected
- npm: `detect-character-encoding` — affected >=0 <0.3.1

## Details
### Impact

In detect-character-encoding v0.3.0 and earlier, allocated memory is not released.

### Patches

The problem has been patched in [detect-character-encoding v0.3.1](https://github.com/sonicdoe/detect-character-encoding/releases/tag/v0.3.1).

### CVSS score

[CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/RL:O/RC:C](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/RL:O/RC:C)

Base Score: 7.5 (High)
Temporal Score: 7.2 (High)

Since detect-character-encoding is a library, the scoring is based on the “[reasonable worst-case implementation scenario](https://www.first.org/cvss/v3.1/user-guide#3-7-Scoring-Vulnerabilities-in-Software-Libraries-and-Similar)”, namely, using detect-character-encoding in a program accessible over the internet which becomes unavailable when running out of memory. Depending on your specific implementation, the vulnerability’s severity in your program may be different.

### Proof of concept

```js
const express = require("express");
const detectCharacterEncoding = require("detect-character-encoding");

const app = express();

app.get("/", (req, res) => {
  detectCharacterEncoding(Buffer.from("foo"));

  res.end();
});

app.listen(3000);
```

`hey -n 1000000 http://localhost:3000` ([`hey`](https://github.com/rakyll/hey)) causes the Node.js process to consume more and more memory.

### References

- https://github.com/sonicdoe/detect-character-encoding/commit/d44356927b92e3b13e178071bf6d7c671766f588
- https://github.com/sonicdoe/detect-character-encoding/pull/6

## References
- https://github.com/sonicdoe/detect-character-encoding/security/advisories/GHSA-5rwj-j5m3-3chj
- https://nvd.nist.gov/vuln/detail/CVE-2021-39176
- https://github.com/sonicdoe/detect-character-encoding/pull/6
- https://github.com/sonicdoe/detect-character-encoding/commit/d44356927b92e3b13e178071bf6d7c671766f588
- https://github.com/sonicdoe/detect-character-encoding
- https://github.com/sonicdoe/detect-character-encoding/releases/tag/v0.3.1
