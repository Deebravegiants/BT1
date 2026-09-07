# [M] PMD Designer has Stored XSS in VBHTMLRenderer and YAHTMLRenderer via unescaped violation messages

## Summary
Severity: Medium
Advisory: GHSA-8rr6-2qw5-pc7r
CVE: CVE-2026-28338
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-8rr6-2qw5-pc7r
Type: github-advisory

## Affected
- Maven: `net.sourceforge.pmd:pmd-core` — affected >=0 <7.22.0

## Details
### Summary
PMD's `vbhtml` and `yahtml` report formats insert rule violation messages into HTML output without escaping. When PMD analyzes untrusted source code containing crafted string literals, the generated HTML report contains executable JavaScript that runs when opened in a browser.

While the default `html` format is not affected via rule violation messages (it correctly uses `StringEscapeUtils.escapeHtml4()`), it has a similar problem when rendering suppressed violations. The user supplied message (the reason for the suppression) was not escaped.

### Details
`VBHTMLRenderer.java` line 71 appends `rv.getDescription()` directly into HTML:

```java
sb.append("<td><font class=body>").append(rv.getDescription()).append("</font></td>");
```

`YAHTMLRenderer.java` lines 196–203 does the same via `renderViolationRow()`:

```java
private String renderViolationRow(String name, String value) {
    return "<tr><td><b>" + name + "</b></td>" + "<td>" + value + "</td></tr>";
}
```

Called at line 172:

```java
out.print(renderViolationRow("Description:", violation.getDescription()));
```

The violation message originates from `AvoidDuplicateLiteralsRule.java` line 91, which embeds raw string literal values via `first.toPrintableString()`. This calls `StringUtil.escapeJava()` (line 476–480), which is a Java source escaper — it passes `<`, `>`, and `&` through unchanged because they are printable ASCII (0x20–0x7e).

By contrast, `HTMLRenderer.java` line 143 properly escapes:

```java
String d = StringEscapeUtils.escapeHtml4(rv.getDescription());
```
### PoC

1. Create a Java file with 4+ duplicate string literals containing an HTML payload:

```java
public class Exploit {
    String a = "<img src=x onerror=alert(document.domain)>";
    String b = "<img src=x onerror=alert(document.domain)>";
    String c = "<img src=x onerror=alert(document.domain)>";
    String d = "<img src=x onerror=alert(document.domain)>";
}
```

2. Run PMD with the `vbhtml` format:

```bash
pmd check -R category/java/errorprone.xml -f vbhtml -d Exploit.java -r report.html
```

3. Open `report.html` in a browser. A JavaScript alert executes showing `document.domain`.

The generated HTML contains the unescaped tag:

```html
<td><font class=body>The String literal "<img src=x onerror=alert(document.domain)>" appears 4 times in this file</font></td>
```

Tested and confirmed on PMD 7.22.0-SNAPSHOT (commit bcc646c53d).

### Impact
Stored cross-site scripting (XSS). Affects CI/CD pipelines that run PMD with `--format vbhtml` or `--format yahtml` on untrusted source code (e.g., pull requests from external contributors) and expose the HTML report as a build artifact. JavaScript executes in the browser context of anyone who opens the report.

Practical impact is limited because `vbhtml` and `yahtml` are legacy formats rarely used in practice. The default `html` format has a similar issue with user messages from suppressed violations.

### Fixes
* See [#6475](https://github.com/pmd/pmd/issues/6475): \[core] Fix stored XSS in VBHTMLRenderer and YAHTMLRenderer

## References
- https://github.com/pmd/pmd/security/advisories/GHSA-8rr6-2qw5-pc7r
- https://nvd.nist.gov/vuln/detail/CVE-2026-28338
- https://github.com/pmd/pmd/pull/6475
- https://github.com/pmd/pmd/commit/c140c0e1de5853a08efb84c9f91dfeb015882442
- https://github.com/pmd/pmd
