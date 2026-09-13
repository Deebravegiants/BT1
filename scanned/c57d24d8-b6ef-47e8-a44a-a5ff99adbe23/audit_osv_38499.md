# [M] Sentry kernel has incomplete ownership check for IRQ line manipulation

## Summary
Severity: Medium
Advisory: CVE-2026-40337
Aliases: GHSA-5hgv-rg2f-79pg
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40337
Type: osv

## Details
The Sentry kernel is a high security level micro-kernel implementation made for high security embedded systems. A given task with one of the DEV or IO capability is able to interact with another task's IRQ line through the __sys_int_* syscall familly. Prior to version 0.4.7, this can lead to DoS and covert-channels between this task and the outer world. A patch is available in version 0.4.7. As a workaround, reduce tasks that have the DEV and IO capability to a single one.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40337.json
- https://github.com/camelot-os/sentry-kernel/security/advisories/GHSA-5hgv-rg2f-79pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-40337
- https://github.com/camelot-os/sentry-kernel/commit/150b7edd2c5b0da0a8baeed3135ddde613b08081
- https://github.com/camelot-os/sentry-kernel/pull/108
