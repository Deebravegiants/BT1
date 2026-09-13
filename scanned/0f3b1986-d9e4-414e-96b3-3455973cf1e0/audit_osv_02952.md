# [M] ALPINE-CVE-2023-5870

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-5870
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5870
Type: osv

## Affected
- Alpine:v3.15: `postgresql14` — affected >=0 <14.10-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.10-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.10-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.10-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.5-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.5-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.5-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.5-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.1-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.1-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.1-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.1-r0

## Details
A flaw was found in PostgreSQL involving the pg_cancel_backend role that signals background workers, including the logical replication launcher, autovacuum workers, and the autovacuum launcher. Successful exploitation requires a non-core extension with a less-resilient background worker and would affect that specific background worker only. This issue may allow a remote high privileged user to launch a denial of service (DoS) attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5870
