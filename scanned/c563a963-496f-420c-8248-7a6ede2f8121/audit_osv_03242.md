# [H] ALPINE-CVE-2025-27516

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-27516
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-03-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27516
Type: osv

## Affected
- Alpine:v3.18: `py3-jinja2` — affected >=0 <3.1.6-r0
- Alpine:v3.19: `py3-jinja2` — affected >=0 <3.1.6-r0
- Alpine:v3.20: `py3-jinja2` — affected >=0 <3.1.6-r0
- Alpine:v3.21: `py3-jinja2` — affected >=0 <3.1.6-r0
- Alpine:v3.22: `py3-jinja2` — affected >=0 <3.1.6-r0
- Alpine:v3.23: `py3-jinja2` — affected >=0 <3.1.6-r0
- Alpine:v3.24: `py3-jinja2` — affected >=0 <3.1.6-r0

## Details
Jinja is an extensible templating engine. Prior to 3.1.6, an oversight in how the Jinja sandboxed environment interacts with the |attr filter allows an attacker that controls the content of a template to execute arbitrary Python code. To exploit the vulnerability, an attacker needs to control the content of a template. Whether that is the case depends on the type of application using Jinja. This vulnerability impacts users of applications which execute untrusted templates. Jinja's sandbox does catch calls to str.format and ensures they don't escape the sandbox. However, it's possible to use the |attr filter to get a reference to a string's plain format method, bypassing the sandbox. After the fix, the |attr filter no longer bypasses the environment's attribute lookup. This vulnerability is fixed in 3.1.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27516
