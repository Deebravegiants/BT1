# [M] ALPINE-CVE-2020-28493

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-28493
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-02-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-28493
Type: osv

## Affected
- Alpine:v3.14: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.15: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.16: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.17: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.18: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.19: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.20: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.21: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.22: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.23: `py3-jinja2` — affected >=0 <1.11.3-r0
- Alpine:v3.24: `py3-jinja2` — affected >=0 <1.11.3-r0

## Details
This affects the package jinja2 from 0.0.0 and before 2.11.3. The ReDoS vulnerability is mainly due to the `_punctuation_re regex` operator and its use of multiple wildcards. The last wildcard is the most exploitable as it searches for trailing punctuation. This issue can be mitigated by Markdown to format user content instead of the urlize filter, or by implementing request timeouts and limiting process memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-28493
