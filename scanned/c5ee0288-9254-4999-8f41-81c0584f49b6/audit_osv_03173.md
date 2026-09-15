# [H] ALPINE-CVE-2024-9287

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-9287
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-9287
Type: osv

## Affected
- Alpine:v3.18: `python3` — affected >=0 <3.11.11-r0
- Alpine:v3.19: `python3` — affected >=0 <3.11.11-r0
- Alpine:v3.20: `python3` — affected >=0 <3.12.8-r0
- Alpine:v3.21: `python3` — affected >=0 <3.12.8-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.8-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.8-r0
- Alpine:v3.24: `python3` — affected >=0 <3.12.8-r0

## Details
A vulnerability has been found in the CPython `venv` module and CLI where path names provided when creating a virtual environment were not quoted properly, allowing the creator to inject commands into virtual environment "activation" scripts (ie "source venv/bin/activate"). This means that attacker-controlled virtual environments are able to run commands when the virtual environment is activated. Virtual environments which are not created by an attacker or which aren't activated before being used (ie "./venv/bin/python") are not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-9287
