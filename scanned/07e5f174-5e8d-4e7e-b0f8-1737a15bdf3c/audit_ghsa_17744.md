# [M] jte's HTML templates containing Javascript template strings are subject to XSS

## Summary
Severity: Medium
Advisory: GHSA-vh22-6c6h-rm8q
CVE: CVE-2025-23026
CWE: CWE-150, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-13
Source: https://github.com/advisories/GHSA-vh22-6c6h-rm8q
Type: github-advisory

## Affected
- Maven: `gg.jte:jte` — affected >=0 <3.1.16
- Maven: `gg.jte:jte-runtime` — affected >=0 <3.1.16

## Details
### Summary
Jte HTML templates with `script` tags or script attributes that include a Javascript template string (backticks) are subject to XSS.

### Details
The `javaScriptBlock` and `javaScriptAttribute` methods in the `Escape` class ([source](https://github.com/casid/jte/blob/main/jte-runtime/src/main/java/gg/jte/html/escape/Escape.java#L43-L83)) do not escape backticks, which are used for Javascript [template strings](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#description). Dollar signs in template strings should also be escaped as well to prevent undesired interpolation.

### PoC
1. Use the [Jte Gradle Plugin](https://jte.gg/gradle-plugin/) with the following code in `src/jte/xss.jte`:
    ```html
    @param String someMessage
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>XSS Test</title>
        <script>window.someVariable = `${someMessage}`;</script>
    </head>
    <body>
    <h1>XSS Test</h1>
    </body>
    </html>
    ```
2. Use the following Java code to demonstrate the XSS vulnerability:
    ```java
    final StringOutput output = new StringOutput();
    JtexssGenerated.render(new OwaspHtmlTemplateOutput(output), null, "` + alert(`xss`) + `");
    renderHtml(output);
    ```

### Impact
HTML templates rendered by Jte's `OwaspHtmlTemplateOutput` in versions less than or equal to `3.1.15` with `script` tags or script attributes that contain Javascript template strings (backticks) are vulnerable.

## References
- https://github.com/casid/jte/security/advisories/GHSA-vh22-6c6h-rm8q
- https://nvd.nist.gov/vuln/detail/CVE-2025-23026
- https://github.com/casid/jte/commit/a6fb00d53c7b8dbb86de933215dbe1b9191a57f1
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#description
- https://github.com/casid/jte
- https://github.com/casid/jte/blob/main/jte-runtime/src/main/java/gg/jte/html/escape/Escape.java#L43-L83
