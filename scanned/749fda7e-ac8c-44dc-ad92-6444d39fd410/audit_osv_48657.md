# [H] CVE-2018-10871

## Summary
Severity: High
Advisory: CVE-2018-10871
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-18
Source: https://osv.dev/vulnerability/CVE-2018-10871
Type: osv

## Details
389-ds-base before versions 1.3.8.5, 1.4.0.12 is vulnerable to a Cleartext Storage of Sensitive Information. By default, when the Replica and/or retroChangeLog plugins are enabled, 389-ds-base stores passwords in plaintext format in their respective changelog files. An attacker with sufficiently high privileges, such as root or Directory Manager, can query these files in order to retrieve plaintext passwords.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00032.html
- https://access.redhat.com/errata/RHSA-2019:3401
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10871
- https://pagure.io/389-ds-base/issue/49789
