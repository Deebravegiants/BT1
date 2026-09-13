# [C] VaahCMS 2.0.0 - 2.3.4 Malicious JavaScript Supply Chain via security-otp.blade.php

## Summary
Severity: Critical
Advisory: CVE-2026-67595
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-67595
Type: osv

## Details
VaahCMS versions 2.0.0 through 2.3.4 contain a malicious obfuscated JavaScript payload embedded in the Blade template responsible for rendering security OTP emails, allowing remote attackers to execute unauthorized code in any browser that renders the affected email template with JavaScript enabled. The payload establishes a WebSocket connection to a hardcoded command-and-control endpoint, installs a password-field keylogger using MutationObserver to capture dynamically added inputs, scrapes WhatsApp Web DOM content, and accepts remote commands to redirect or overwrite the rendered page.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67595.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67595
- https://www.vulncheck.com/advisories/vaahcms-malicious-javascript-supply-chain-via-security-otp-blade-php
- https://github.com/webreinvent/vaahcms/pull/317
- https://github.com/webreinvent/vaahcms/commit/8d7898f7a385a5fade1180a9b664ff158d873129
- https://github.com/webreinvent/vaahcms
