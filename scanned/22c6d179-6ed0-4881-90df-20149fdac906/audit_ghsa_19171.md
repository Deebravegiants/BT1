# [H] S3-Proxy allows Reflected Cross-site Scripting (XSS) in template implementation

## Summary
Severity: High
Advisory: GHSA-pp9m-qf39-hxjc
CVE: CVE-2025-27088
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-02-20
Source: https://github.com/advisories/GHSA-pp9m-qf39-hxjc
Type: github-advisory

## Affected
- Go: `github.com/oxyno-zeta/s3-proxy/cmd/s3-proxy` — affected >=0 <0.0.0-20250220214310-c611c741ed48

## Details
### Summary
A Reflected Cross-site Scripting (XSS) vulnerability enables attackers to create malicious URLs that, when visited, inject scripts into the web application. This can lead to session hijacking or phishing attacks on a trusted domain, posing a high risk to all users.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._
It's possible to inject html elements, including scripts through the [folder-list template](https://github.com/oxyno-zeta/s3-proxy/blob/master/templates/folder-list.tpl#L19C21-L19C38). It seems like the `.Request.URL.Path` variable is not escaped.

I did some research and found it might be due to the `text/template` import being used in [the template implementation](https://github.com/oxyno-zeta/s3-proxy/blob/master/pkg/s3-proxy/utils/templateutils/template.go#L8), instead of the [safer](https://pkg.go.dev/html/template) `html/template`.

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._
Using the [default template configuration](https://oxyno-zeta.github.io/s3-proxy/configuration/structure/#targettemplateconfig), the vulnerability can be reproduced with the following steps.

1. Navigate to `https://your-s3-proxy.com/path-not-found` and confirm the page looks as follows:
![image](https://github.com/user-attachments/assets/1c87e274-18ec-4eb3-94fe-25bb1c0abf37)

2. Try inserting an HTML element by changing `/path-not-found` to `/<img src="x">` and confirm the page looks as follows:
![image](https://github.com/user-attachments/assets/19c80f46-c406-4e5f-81f3-16103bc963b8)

3. Now it should be possible to run any JavaScript by manipulating the [`onerror` property of the img element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#image_loading_errors). This should make the link look like `https://your-s3-proxy.com/<img src="x" onerror="alert(1)">`. Confirm that going to this URL will in fact shows an alert in the browser.

### Impact
The affected template allows users to interact with the URL path provided by the `Request.URL.Path` variable, which is then rendered directly into the HTML without proper sanitization or escaping. This can be abused by attackers who craft a malicious URL containing injected HTML or JavaScript. When users visit such a URL, the malicious script will be executed in the user's context, leading to potential risks such as:
- **Session Hijacking**: Malicious scripts could be used to steal session cookies or other sensitive information.
- **Phishing Attacks**: JavaScript could be injected to trick users into submitting sensitive information, such as login credentials.

This vulnerability can be exploited by attackers who craft URLs containing malicious payloads, which would then execute in the user's browser when they access the affected page. This poses a **high** risk to all users who visit such URLs.

## References
- https://github.com/oxyno-zeta/s3-proxy/security/advisories/GHSA-pp9m-qf39-hxjc
- https://nvd.nist.gov/vuln/detail/CVE-2025-27088
- https://github.com/oxyno-zeta/s3-proxy/commit/c611c741ed4872ea3f46232be23bb830f96f9564
- https://github.com/oxyno-zeta/s3-proxy
- https://github.com/oxyno-zeta/s3-proxy/blob/master/templates/folder-list.tpl#L19C21-L19C38
- https://github.com/oxyno-zeta/s3-proxy/releases/tag/v4.18.1
