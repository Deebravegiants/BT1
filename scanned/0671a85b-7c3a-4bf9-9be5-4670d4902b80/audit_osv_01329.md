# [M] ALPINE-CVE-2019-10217

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-10217
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10217
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.8.0 <2.8.4-r0
- Alpine:v3.11: `ansible` — affected >=2.8.0 <2.8.4-r0
- Alpine:v3.12: `ansible` — affected >=2.8.0 <2.8.4-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.8.4-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.8.4-r0

## Details
A flaw was found in ansible 2.8.0 before 2.8.4. Fields managing sensitive data should be set as such by no_log feature. Some of these fields in GCP modules are not set properly. service_account_contents() which is common class for all gcp modules is not setting no_log to True. Any sensitive data managed by that function would be leak as an output when running ansible playbooks.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10217
