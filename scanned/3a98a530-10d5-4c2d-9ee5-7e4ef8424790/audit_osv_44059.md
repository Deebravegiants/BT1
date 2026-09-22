# [C] zbus_polkit: polkit authorization bypass via PID reuse due to incorrect D-Bus type for the subject UID

## Summary
Severity: Critical
Advisory: CVE-2026-78422
Aliases: RUSTSEC-2026-0278
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-78422
Type: osv

## Details
Subject::new_for_owner() in the zbus_polkit crate encodes the uid entry of a unix-process polkit subject as an unsigned 32-bit integer (D-Bus type u), whereas the org.freedesktop.PolicyKit1.Authority interface specifies a signed 32-bit integer (D-Bus type i). Because of this type mismatch, polkit silently discards the caller-supplied UID and instead determines the subject's owner itself by looking up the PID in /proc, a lookup that is inherently subject to a time-of-check/time-of-use race.

Consequently, an application that passes a UID obtained from a trustworthy source — for example SO_PEERCRED Unix socket peer credentials — in order to defend against PID reuse receives no protection, and the supplied UID has no effect on the authorization decision. A local unprivileged attacker who can cause an authorized process to terminate and then win the race to have their own process assigned the same PID can be authorized under the identity of the terminated process, bypassing the polkit authorization check and performing actions the attacker is not entitled to.

This issue affects zbus_polkit before 5.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78422.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78422
- https://bugzilla.suse.com/show_bug.cgi?id=1277659
- https://github.com/z-galaxy/zbus_polkit/pull/101
- https://github.com/z-galaxy/zbus_polkit
