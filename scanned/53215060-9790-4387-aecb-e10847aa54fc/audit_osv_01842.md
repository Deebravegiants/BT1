# [C] ALPINE-CVE-2020-1747

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-1747
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1747
Type: osv

## Affected
- Alpine:v3.11: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.12: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.13: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.14: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.15: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.16: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.17: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.18: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.19: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.20: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.21: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.22: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.23: `py3-yaml` — affected >=0 <5.3.1-r0
- Alpine:v3.24: `py3-yaml` — affected >=0 <5.3.1-r0

## Details
A vulnerability was discovered in the PyYAML library in versions before 5.3.1, where it is susceptible to arbitrary code execution when it processes untrusted YAML files through the full_load method or with the FullLoader loader. Applications that use the library to process untrusted input may be vulnerable to this flaw. An attacker could use this flaw to execute arbitrary code on the system by abusing the python/object/new constructor.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1747
