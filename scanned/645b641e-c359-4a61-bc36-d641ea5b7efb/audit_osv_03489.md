# [H] ALPINE-CVE-2026-20716

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-20716
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-20716
Type: osv

## Affected
- Alpine:v3.21: `intel-ucode` — affected >=0 <20260812-r0
- Alpine:v3.22: `intel-ucode` — affected >=0 <20260812-r0
- Alpine:v3.23: `intel-ucode` — affected >=0 <20260812-r0
- Alpine:v3.24: `intel-ucode` — affected >=0 <20260812-r0

## Details
Improper access control for some Intel(R) Processors within Ring 3: User Applications may allow an escalation of privilege. Simple hardware adversary with an authenticated user combined with a high complexity attack may enable escalation of privilege. This result may potentially occur via local access when attack requirements are present with special internal knowledge and requires no user interaction. The potential vulnerability may impact the confidentiality (high), integrity (high) and availability (none) of the vulnerable system, resulting in subsequent system confidentiality (none), integrity (none) and availability (none) impacts.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-20716
