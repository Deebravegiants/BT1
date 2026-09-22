# [H] ALPINE-CVE-2015-8325

## Summary
Severity: High
Advisory: ALPINE-CVE-2015-8325
Ecosystem: Alpine:v3.2
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-8325
Type: osv

## Affected
- Alpine:v3.2: `openssh` — affected >=0 <6.8_p1-r10

## Details
The do_setup_env function in session.c in sshd in OpenSSH through 7.2p2, when the UseLogin feature is enabled and PAM is configured to read .pam_environment files in user home directories, allows local users to gain privileges by triggering a crafted environment for the /bin/login program, as demonstrated by an LD_PRELOAD environment variable.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-8325
