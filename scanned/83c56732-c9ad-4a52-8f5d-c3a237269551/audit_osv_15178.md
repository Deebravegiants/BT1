# [H] CVE-2019-14287

## Summary
Severity: High
Advisory: CVE-2019-14287
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-17
Source: https://osv.dev/vulnerability/CVE-2019-14287
Type: osv

## Details
In Sudo before 1.8.28, an attacker with access to a Runas ALL sudoer account can bypass certain policy blacklists and session PAM modules, and can cause incorrect logging, by invoking sudo with a crafted user ID. For example, this allows bypass of !root configuration, and USER= logging, for a "sudo -u \#$((0xffffffff))" command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IP7SIOAVLSKJGMTIULX52VQUPTVSC43U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NPLAM57TPJQGKQMNG6RHFBLACD6K356N/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TUVAOZBYUHZS56A5FQSCDVGXT7PW7FL2/
- https://support.f5.com/csp/article/K53746212?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00047.html
- http://packetstormsecurity.com/files/154853/Slackware-Security-Advisory-sudo-Updates.html
- http://www.openwall.com/lists/oss-security/2019/10/24/1
- http://www.openwall.com/lists/oss-security/2019/10/29/3
- http://www.openwall.com/lists/oss-security/2021/09/14/2
- https://access.redhat.com/errata/RHBA-2019:3248
- https://access.redhat.com/errata/RHSA-2019:3197
- https://access.redhat.com/errata/RHSA-2019:3204
- https://access.redhat.com/errata/RHSA-2019:3205
- https://access.redhat.com/errata/RHSA-2019:3209
- https://access.redhat.com/errata/RHSA-2019:3219
- https://access.redhat.com/errata/RHSA-2019:3278
- https://access.redhat.com/errata/RHSA-2019:3694
- https://access.redhat.com/errata/RHSA-2019:3754
- https://access.redhat.com/errata/RHSA-2019:3755
