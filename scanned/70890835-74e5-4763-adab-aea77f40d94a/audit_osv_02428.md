# [H] ALPINE-CVE-2022-2309

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-2309
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2309
Type: osv

## Affected
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.14-r1
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.14-r1
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.14-r1
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.14-r1
- Alpine:v3.17: `libxml2` — affected >=0 <2.10.0-r0
- Alpine:v3.18: `libxml2` — affected >=0 <2.10.0-r0
- Alpine:v3.19: `libxml2` — affected >=0 <2.10.0-r0
- Alpine:v3.20: `libxml2` — affected >=0 <2.10.0-r0
- Alpine:v3.21: `libxml2` — affected >=0 <2.10.0-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.10.0-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.10.0-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.10.0-r0
- Alpine:v3.17: `py3-lxml` — affected >=0 <4.9.2-r0
- Alpine:v3.18: `py3-lxml` — affected >=0 <4.9.2-r0
- Alpine:v3.19: `py3-lxml` — affected >=0 <4.9.2-r0
- Alpine:v3.20: `py3-lxml` — affected >=0 <4.9.2-r0
- Alpine:v3.21: `py3-lxml` — affected >=0 <4.9.2-r0
- Alpine:v3.22: `py3-lxml` — affected >=0 <4.9.2-r0
- Alpine:v3.23: `py3-lxml` — affected >=0 <4.9.2-r0
- Alpine:v3.24: `py3-lxml` — affected >=0 <4.9.2-r0

## Details
NULL Pointer Dereference allows attackers to cause a denial of service (or application crash). This only applies when lxml is used together with libxml2 2.9.10 through 2.9.14. libxml2 2.9.9 and earlier are not affected. It allows triggering crashes through forged input data, given a vulnerable code sequence in the application. The vulnerability is caused by the iterwalk function (also used by the canonicalize function). Such code shouldn't be in wide-spread use, given that parsing + iterwalk would usually be replaced with the more efficient iterparse function. However, an XML converter that serialises to C14N would also be vulnerable, for example, and there are legitimate use cases for this code sequence. If untrusted input is received (also remotely) and processed via iterwalk function, a crash can be triggered.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2309
