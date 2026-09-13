# [M] bubblewrap vulnerable to privilege escalation in setuid mode via ptrace

## Summary
Severity: Medium
Advisory: CVE-2026-41163
Aliases: GHSA-xq78-7hw4-5jvp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-09
Source: https://osv.dev/vulnerability/CVE-2026-41163
Type: osv

## Details
bubblewrap is a low-level unprivileged sandboxing tool. From version 0.11.0 to before version 0.11.2, if bubblewrap is installed in setuid mode then the user can use ptrace to attach to bubblewrap and control the unprivileged part of the sandbox setup phase. This allows the attacker to arbitrarily use the privileged operations, and in particular the "overlay mount" operation, allowing the creation of overlay mounts which is otherwise not allowed in the setuid version of bubblewrap. This issue has been patched in version 0.11.2.

## References
- https://github.com/containers/bubblewrap/releases/tag/v0.11.2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41163.json
- https://access.redhat.com/security/cve/CVE-2026-41163
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41163.json
- https://github.com/containers/bubblewrap/security/advisories/GHSA-xq78-7hw4-5jvp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41163
- https://bugzilla.redhat.com/show_bug.cgi?id=2468439
