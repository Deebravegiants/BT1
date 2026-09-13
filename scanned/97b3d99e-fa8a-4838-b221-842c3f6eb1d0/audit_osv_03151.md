# [C] ALPINE-CVE-2024-56326

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-56326
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2024-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-56326
Type: osv

## Affected
- Alpine:v3.18: `py3-jinja2` — affected >=0 <3.1.5-r0
- Alpine:v3.19: `py3-jinja2` — affected >=0 <3.1.5-r0
- Alpine:v3.20: `py3-jinja2` — affected >=0 <3.1.5-r0
- Alpine:v3.21: `py3-jinja2` — affected >=0 <3.1.5-r0
- Alpine:v3.22: `py3-jinja2` — affected >=0 <3.1.5-r0
- Alpine:v3.23: `py3-jinja2` — affected >=0 <3.1.5-r0
- Alpine:v3.24: `py3-jinja2` — affected >=0 <3.1.5-r0

## Details
Jinja is an extensible templating engine. Prior to 3.1.5, An oversight in how the Jinja sandboxed environment detects calls to str.format allows an attacker that controls the content of a template to execute arbitrary Python code. To exploit the vulnerability, an attacker needs to control the content of a template. Whether that is the case depends on the type of application using Jinja. This vulnerability impacts users of applications which execute untrusted templates. Jinja's sandbox does catch calls to str.format and ensures they don't escape the sandbox. However, it's possible to store a reference to a malicious string's format method, then pass that to a filter that calls it. No such filters are built-in to Jinja, but could be present through custom filters in an application. After the fix, such indirect calls are also handled by the sandbox. This vulnerability is fixed in 3.1.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-56326
