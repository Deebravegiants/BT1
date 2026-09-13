# [M] Stored Cross-Site Scripting via Untrusted Cryptocurrency Address Rendering in RansomLook

## Summary
Severity: Medium
Advisory: CVE-2026-78391
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78391
Type: osv

## Details
RansomLook contains a stored cross-site scripting (XSS) vulnerability in the cryptocurrency wallet detail view. Cryptocurrency addresses and blockchain names originating from external sources, including the public crowd-sourced ransomwhe.re feed, were stored without sufficient validation and later embedded directly into an inline JavaScript onclick handler.


Although Jinja HTML autoescaping was applied, it does not provide adequate protection when untrusted data is inserted into a JavaScript string inside an HTML attribute. HTML entities such as &#39; are decoded by the browser's HTML parser before the resulting attribute is interpreted as JavaScript. Consequently, a specially crafted cryptocurrency address containing quote characters and JavaScript syntax could escape the intended string literal and execute arbitrary JavaScript when a user clicked the affected wallet's CSV export button.


Because cryptocurrency information imported from an untrusted upstream could reach the vulnerable rendering path, exploitation may not require an authenticated RansomLook account if an attacker can introduce a malicious wallet record into a consumed external data source. Successful exploitation could allow attacker-controlled JavaScript to execute in the security context of the RansomLook web application, potentially exposing information accessible to the victim or performing actions with the victim's privileges.


The patch mitigates the issue by validating cryptocurrency addresses and blockchain identifiers before storage, restricting them to a safe character set, and replacing the inline JavaScript handler with data-* attributes and an external event listener so wallet values are treated strictly as data rather than executable JavaScript.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78391.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78391
- https://github.com/RansomLook/RansomLook/commit/7efb59253f23552538f9a11c9bf21e7bcfcc1319
- https://github.com/RansomLook/RansomLook
