# [H] ALPINE-CVE-2023-49298

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-49298
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-11-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49298
Type: osv

## Affected
- Alpine:v3.19: `zfs` — affected >=0 <2.2.1-r1
- Alpine:v3.20: `zfs` — affected >=0 <2.2.1-r1
- Alpine:v3.21: `zfs` — affected >=0 <2.2.1-r1
- Alpine:v3.22: `zfs` — affected >=0 <2.2.1-r1
- Alpine:v3.23: `zfs` — affected >=0 <2.2.1-r1
- Alpine:v3.24: `zfs` — affected >=0 <2.2.1-r1
- Alpine:v3.19: `zfs-lts` — affected >=0 <2.2.1-r1
- Alpine:v3.20: `zfs-lts` — affected >=0 <2.2.1-r1
- Alpine:v3.21: `zfs-lts` — affected >=0 <2.2.1-r1
- Alpine:v3.22: `zfs-lts` — affected >=0 <2.2.1-r1
- Alpine:v3.23: `zfs-lts` — affected >=0 <2.2.1-r1
- Alpine:v3.24: `zfs-lts` — affected >=0 <2.2.1-r1
- Alpine:v3.19: `zfs-rpi` — affected >=0 <2.2.1-r1
- Alpine:v3.20: `zfs-rpi` — affected >=0 <2.2.1-r1
- Alpine:v3.21: `zfs-rpi` — affected >=0 <2.2.1-r1
- Alpine:v3.22: `zfs-rpi` — affected >=0 <2.2.1-r1
- Alpine:v3.23: `zfs-rpi` — affected >=0 <2.2.1-r1
- Alpine:v3.24: `zfs-rpi` — affected >=0 <2.2.1-r1

## Details
OpenZFS through 2.1.13 and 2.2.x through 2.2.1, in certain scenarios involving applications that try to rely on efficient copying of file data, can replace file contents with zero-valued bytes and thus potentially disable security mechanisms. NOTE: this issue is not always security related, but can be security related in realistic situations. A possible example is cp, from a recent GNU Core Utilities (coreutils) version, when attempting to preserve a rule set for denying unauthorized access. (One might use cp when configuring access control, such as with the /etc/hosts.deny file specified in the IBM Support reference.) NOTE: this issue occurs less often in version 2.2.1, and in versions before 2.1.4, because of the default configuration in those versions.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49298
