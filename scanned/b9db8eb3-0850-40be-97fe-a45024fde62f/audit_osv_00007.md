# [M] ALPINE-CVE-2014-3230

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2014-3230
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2014-3230
Type: osv

## Affected
- Alpine:v3.19: `perl-lwp-protocol-https` — affected >=0 <6.11-r0
- Alpine:v3.20: `perl-lwp-protocol-https` — affected >=0 <6.11-r0
- Alpine:v3.21: `perl-lwp-protocol-https` — affected >=0 <6.11-r0
- Alpine:v3.22: `perl-lwp-protocol-https` — affected >=0 <6.11-r0
- Alpine:v3.23: `perl-lwp-protocol-https` — affected >=0 <6.11-r0
- Alpine:v3.24: `perl-lwp-protocol-https` — affected >=0 <6.11-r0

## Details
The libwww-perl LWP::Protocol::https module 6.04 through 6.06 for Perl, when using IO::Socket::SSL as the SSL socket class, allows attackers to disable server certificate validation via the (1) HTTPS_CA_DIR or (2) HTTPS_CA_FILE environment variable.

## References
- https://security.alpinelinux.org/vuln/CVE-2014-3230
