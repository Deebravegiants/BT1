# [H] CVE-2019-3883

## Summary
Severity: High
Advisory: CVE-2019-3883
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-17
Source: https://osv.dev/vulnerability/CVE-2019-3883
Type: osv

## Details
In 389-ds-base up to version 1.4.1.2, requests are handled by workers threads. Each sockets will be waited by the worker for at most 'ioblocktimeout' seconds. However this timeout applies only for un-encrypted requests. Connections using SSL/TLS are not taking this timeout into account during reads, and may hang longer.An unauthenticated attacker could repeatedly create hanging LDAP requests to hang all the workers, resulting in a Denial of Service.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00026.html
- https://access.redhat.com/errata/RHSA-2019:1896
- https://access.redhat.com/errata/RHSA-2019:3401
- https://lists.debian.org/debian-lts-announce/2019/05/msg00008.html
- https://pagure.io/389-ds-base/pull-request/50331
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3883
- https://pagure.io/389-ds-base/issue/50329
