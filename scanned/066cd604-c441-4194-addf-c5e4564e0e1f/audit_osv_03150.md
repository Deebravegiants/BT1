# [H] ALPINE-CVE-2024-56201

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-56201
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-56201
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
Jinja is an extensible templating engine. In versions on the 3.x branch prior to 3.1.5, a bug in the Jinja compiler allows an attacker that controls both the content and filename of a template to execute arbitrary Python code, regardless of if Jinja's sandbox is used. To exploit the vulnerability, an attacker needs to control both the filename and the contents of a template. Whether that is the case depends on the type of application using Jinja. This vulnerability impacts users of applications which execute untrusted templates where the template author can also choose the template filename. This vulnerability is fixed in 3.1.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-56201
