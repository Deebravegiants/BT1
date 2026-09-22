# [H] ALPINE-CVE-2022-3996

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-3996
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3996
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.7-r2
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.0.7-r2
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.0.7-r2
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.0.7-r2
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.0.7-r2
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.0.7-r2
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.0.7-r2
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.0.7-r2
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r0

## Details
If an X.509 certificate contains a malformed policy constraint and
policy processing is enabled, then a write lock will be taken twice
recursively.  On some operating systems (most widely: Windows) this
results in a denial of service when the affected process hangs.  Policy
processing being enabled on a publicly facing server is not considered
to be a common setup.

Policy processing is enabled by passing the `-policy'
argument to the command line utilities or by calling the
`X509_VERIFY_PARAM_set1_policies()' function.

Update (31 March 2023): The description of the policy processing enablement
was corrected based on CVE-2023-0466.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3996
