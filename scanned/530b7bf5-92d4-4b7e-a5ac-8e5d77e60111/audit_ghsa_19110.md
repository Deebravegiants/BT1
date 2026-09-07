# [M] Label Studio allows Cross-Site Scripting (XSS) via GET request to `/projects/upload-example` endpoint

## Summary
Severity: Medium
Advisory: GHSA-wpq5-3366-mqw4
CVE: CVE-2025-25296
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-wpq5-3366-mqw4
Type: github-advisory

## Affected
- PyPI: `label-studio` — affected >=0 <1.16.0

## Details
## Description
Label Studio's `/projects/upload-example` endpoint allows injection of arbitrary HTML through a `GET` request with an appropriately crafted `label_config` query parameter. By crafting a specially formatted XML label config with inline task data containing malicious HTML/JavaScript, an attacker can achieve Cross-Site Scripting (XSS). While the application has a Content Security Policy (CSP), it is only set in report-only mode, making it ineffective at preventing script execution.

The vulnerability exists because the upload-example endpoint renders user-provided HTML content without proper sanitization on a GET request. This allows attackers to inject and execute arbitrary JavaScript in victims' browsers by getting them to visit a maliciously crafted URL.

This is considered vulnerable because it enables attackers to execute JavaScript in victims' contexts, potentially allowing theft of sensitive data, session hijacking, or other malicious actions.

## Steps to reproduce
1. Create a malicious label config that includes an XSS payload in embedded task data:

```xml
<View><!-- {"data": {"text": "<div><img src=x
onerror=eval(atob(`YWxlcnQoIlhTUyIp`))></div>"}} --><HyperText name="text"
value="$text"/></View>
```


2. URL encode the payload and access the following URL:

- http://app/projects/upload-example/?label_config=%3CView%3E%3C!--%20{%22data%22:%20{%22text%22:%20%22%3Cdiv%3E%3Cimg%20src=x%20onerror=eval(atob(`YWxlcnQoIlhTUyIp`))%3E%3C/div%3E%22}}%20--%3E%3CHyperText%20name=%22text%22%20value=%22$text%22/%3E%3C/View%3E

When executed, the payload causes the application to render an HTML page containing an img tag that fails to load, triggering the onerror event handler which executes base64-decoded JavaScript, demonstrating successful XSS execution in the victim's browser.
   
## Mitigations
- Enable the Content Security Policy in enforcement mode instead of report-only mode to actively block unauthorized script execution
- Deprecate the `GET` behavior at the `example-config` endpoint since it's not used 

## Impact
The vulnerability requires no special privileges and can be exploited by getting a victim to visit a crafted URL. The impact is high as it allows arbitrary JavaScript execution in victims' browsers, potentially exposing sensitive data or enabling account takeover through session theft.

## References
- https://github.com/HumanSignal/label-studio/security/advisories/GHSA-wpq5-3366-mqw4
- https://nvd.nist.gov/vuln/detail/CVE-2025-25296
- https://github.com/HumanSignal/label-studio/commit/8cf6958e1e27ef6a03ed287e674470975d340885
- https://github.com/HumanSignal/label-studio
