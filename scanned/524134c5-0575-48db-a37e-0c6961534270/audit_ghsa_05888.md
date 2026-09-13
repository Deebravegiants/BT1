# [H] Kestra vulnerable to stored XSS via custom Markdown [[link]] attribute injection

## Summary
Severity: High
Advisory: GHSA-34pm-923j-7wf8
CVE: CVE-2026-55839
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-34pm-923j-7wf8
Type: github-advisory

## Affected
- Maven: `io.kestra:kestra` — affected >=0 <1.3.24

## Details
## Summary

Kestra’s Markdown renderer supports a custom `[[link ...]]` syntax that is converted into a custom HTML element. The custom Markdown parser allows attacker-controlled attributes to be rendered into the generated element without proper allowlisting or sanitization.

As a result, a user who can create or edit Markdown-rendered content, such as a Flow description, can inject JavaScript event-handler attributes. When another user views or interacts with the affected Markdown-rendered UI element, the JavaScript executes in that user’s browser.

This is not a normal raw-HTML Markdown payload such as `<img onerror=...>`. The payload uses Kestra’s custom `[[link]]` Markdown syntax, and the dangerous HTML attributes are introduced by Kestra’s own Markdown plugin.

## Affected version

Tested on Kestra `1.3.22`.

## Affected components

Source review identified the issue in the custom Markdown link renderer:

* `ui/src/utils/markdown_plugins/link.ts`
* `ui/src/utils/markdown.ts`
* `ui/src/components/layout/Markdown.vue`

The vulnerable code path renders parsed attributes directly into an HTML string:

```ts
const attrs = token.attrs
  ? token.attrs.map(([name, value]) => `${name}="${value}"`).join("")
  : "";

return `<router-md ${attrs}>`;
```

The implementation does not safely restrict attribute names or values before inserting the generated HTML into the DOM.

## Proof of concept

Create or edit a Flow with the following YAML:

```yaml
id: markdown_xss_flow_desc
namespace: company.team
description: |
  [[link x="y" style="position:fixed;inset:0;z-index:9999;background:rgba(255,0,0,0.05)" onmouseover="alert(document.domain)"]]

tasks:
  - id: hello
    type: io.kestra.plugin.core.log.Log
    message: hello
```

Save the Flow.

Then navigate to the Flow list:

```text
http://localhost:8080/ui/main/flows
```

Click the description/info icon next to the malicious Flow.

## Actual result

The browser executes JavaScript from the Flow description. In the PoC, an alert is triggered showing the current domain.

## Expected result

Markdown-rendered Flow descriptions should not be able to inject arbitrary JavaScript event handlers or attacker-controlled HTML attributes into the page.

The custom `[[link]]` syntax should only generate safe attributes required for the intended router-link behavior.

## Security impact

An attacker with permission to create or update a Flow in a namespace can store a malicious Markdown payload in the Flow description. When another Kestra user views the Flow list and opens the Flow description/info panel, attacker-controlled JavaScript executes in the victim’s browser.

Depending on the victim’s privileges, this may allow the attacker to perform actions as the victim within the Kestra UI, access data visible to the victim, or pivot into more privileged namespace or administrative functionality.

This crosses a security boundary in multi-user Kestra deployments where Flow authors are less privileged than administrators or other operators who review workflows.

## Suggested remediation

The custom Markdown link plugin should not render arbitrary attributes into raw HTML.

Recommended fixes:

1. Allowlist only the exact attributes required by the custom router link component.
2. Reject all attributes beginning with `on`, such as `onclick`, `onmouseover`, and `onfocus`.
3. Reject or sanitize dangerous attributes such as `style`.
4. HTML-escape all attribute values before rendering.
5. Ensure attributes are joined safely with spaces.
6. Sanitize the final rendered Markdown output before passing it to `v-html`.
7. Add regression tests for custom `[[link]]` payloads containing event-handler attributes.

## Minimal payload

```md
[[link x="y" style="position:fixed;inset:0;z-index:9999;background:rgba(255,0,0,0.05)" onmouseover="alert(document.domain)"]]
```

## Evidence collected

* The payload was stored in a Flow description.
* The Flow list displayed the malicious Flow.
* Opening the Flow description/info panel triggered JavaScript execution in the browser.
* The payload did not require execution of the Flow.
* The payload used Kestra’s custom `[[link]]` syntax rather than raw HTML.

## References
- https://github.com/kestra-io/kestra/security/advisories/GHSA-34pm-923j-7wf8
- https://github.com/kestra-io/kestra/commit/6c8e6d099ed172cbb6b003b7fb30b7bb1f8f710e
- https://github.com/kestra-io/kestra
- https://github.com/kestra-io/kestra/releases/tag/v1.3.24
