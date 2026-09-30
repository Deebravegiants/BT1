# [M] ALPINE-CVE-2016-6210

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-6210
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6210
Type: osv

## Affected
- Alpine:v3.2: `openssh` — affected >=0 <6.8_p1-r7
- Alpine:v3.3: `openssh` — affected >=0 <7.2_p2-r1
- Alpine:v3.4: `openssh` — affected >=0 <7.2_p2-r1

## Details
sshd in OpenSSH before 7.3, when SHA256 or SHA512 are used for user password hashing, uses BLOWFISH hashing on a static password when the username does not exist, which allows remote attackers to enumerate users by leveraging the timing difference between responses when a large password is provided.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6210
