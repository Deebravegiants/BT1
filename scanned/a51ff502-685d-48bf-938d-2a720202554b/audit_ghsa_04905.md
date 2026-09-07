# [M] Allure Report: Stored XSS via unescaped ANSI helper in status message/trace rendering

## Summary
Severity: Medium
Advisory: GHSA-gx93-m64w-5m6h
CVE: CVE-2026-55847
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-gx93-m64w-5m6h
Type: github-advisory

## Affected
- Maven: `io.qameta.allure:allure-generator` — affected >=0 <2.39.0

## Details
## Summary

The `ansi.js` Handlebars helper in allure-generator passes user-controlled `statusMessage` and `statusTrace` values from test result files through the `ansi-to-html` library and wraps the output in Handlebars `SafeString` without HTML escaping. Since `ansi-to-html` does not escape HTML entities by default, an attacker who can influence test result content (e.g., via crafted JUnit XML failure messages) can inject arbitrary JavaScript that executes when anyone views the generated Allure report.

## Details

The vulnerability is an incomplete fix — commit `4c64b19` (PR #3271) fixed XSS in `linky.js` and `text-with-links.js` by adding `escapeExpression()`, but the same pattern in `ansi.js` was not addressed.

**Vulnerable sink** — `allure-generator/src/main/javascript/helpers/ansi.js:10-11`:
```javascript
export default function (input) {
    return new SafeString(ansiConverter.toHtml(input));
};
```

The `AnsiToHtml` constructor at line 4 does not set `escapeForHtml: true`:
```javascript
const ansiConverter = new AnsiToHtml({
    fg: "black",
    bg: "black",
    newline: true,
});
```

The `ansi-to-html` library (v0.7.2) defaults `escapeForHtml` to `false`, meaning HTML entities in the input pass through unchanged. Wrapping the result in `SafeString` tells Handlebars to skip its auto-escaping, so the raw HTML reaches the browser.

**Template usage** — `allure-generator/src/main/javascript/blocks/status-details/status-details.hbs:7,10`:
```handlebars
<pre class="status-details__message"><code>{{ansi statusMessage}}</code></pre>
...
<pre class="{{b 'status-details' 'trace'}}"><code>{{ansi statusTrace}}</code></pre>
```

**Source** — `plugins/junit-xml-plugin/src/main/java/io/qameta/allure/junitxml/JunitXmlPlugin.java:307-308`:
```java
result.setStatusMessage(element.getAttribute(MESSAGE_ATTRIBUTE_NAME));
result.setStatusTrace(element.getValue());
```

These values are read directly from XML attributes with no sanitization. The same pattern exists in TRX, xUnit XML, xctest, and Allure1/2 plugins.

**Contrast with the fixed helper** — `linky.js` (post-fix) correctly escapes before wrapping in `SafeString`:
```javascript
const safeText = escapeExpression(text);
return new SafeString(`<a href="${safeText}" ...>${safeText}</a>`);
```

## PoC

1. Create a malicious JUnit XML test result file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="XSSTest" tests="1" failures="1">
  <testcase name="xssPayload" classname="com.example.Test">
    <failure message="&lt;img src=x onerror=alert(document.cookie)&gt;">
      Stack trace: &lt;img src=x onerror=alert('statusTrace_XSS')&gt;
    </failure>
  </testcase>
</testsuite>
```

2. Generate an Allure report:

```bash
allure generate /path/to/results-with-malicious-xml -o /tmp/allure-report
```

3. Open the report and navigate to the failed test case:

```bash
allure open /tmp/allure-report
```

4. When viewing the test's status details, the `<img onerror>` payloads execute JavaScript in the viewer's browser.

## Impact

- **Arbitrary JavaScript execution** in the browser of anyone viewing the generated Allure report
- **Cookie theft, session hijacking** if the report is served from a domain with active sessions (e.g., CI dashboards)
- **Data exfiltration** — the injected script can read the full report content and send it to an attacker-controlled server
- **Attack vectors**: A malicious dependency that throws crafted exception messages, a CI pipeline processing test results from untrusted pull requests, or a contributor submitting test files containing XSS payloads
- Allure reports are commonly hosted on CI/CD platforms (Jenkins, GitLab, GitHub Actions artifacts) where session cookies may be present

## Recommended Fix

Configure `AnsiToHtml` with `escapeForHtml: true` to escape HTML entities while preserving ANSI-to-HTML conversion:

```javascript
import AnsiToHtml from "ansi-to-html";
import {SafeString} from "handlebars/runtime";

const ansiConverter = new AnsiToHtml({
    fg: "black",
    bg: "black",
    newline: true,
    escapeForHtml: true,  // Escape HTML entities in non-ANSI input
});

export default function (input) {
    return new SafeString(ansiConverter.toHtml(input));
};
```

This is the correct approach because it preserves the ANSI escape sequence → HTML conversion (colored output) while ensuring that any non-ANSI HTML in the input is safely escaped. The alternative of using `escapeExpression()` on the input would destroy ANSI sequences before they could be converted.

## References
- https://github.com/allure-framework/allure2/security/advisories/GHSA-gx93-m64w-5m6h
- https://github.com/allure-framework/allure2
