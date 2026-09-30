# [H] Use After Free in libfuse

## Summary
Severity: High
Advisory: CVE-2026-33150
Aliases: GHSA-qxv7-xrc2-qmfx
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33150
Type: osv

## Details
libfuse is the reference implementation of the Linux FUSE. From version 3.18.0 to before version 3.18.2, a use-after-free vulnerability in the io_uring subsystem of libfuse allows a local attacker to crash FUSE filesystem processes and potentially execute arbitrary code. When io_uring thread creation fails due to resource exhaustion (e.g., cgroup pids.max), fuse_uring_start() frees the ring pool structure but stores the dangling pointer in the session state, leading to a use-after-free when the session shuts down. The trigger is reliable in containerized environments where cgroup pids.max limits naturally constrain thread creation. This issue has been patched in version 3.18.2.

## References
- https://github.com/libfuse/libfuse/releases/tag/fuse-3.18.2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33150.json
- https://access.redhat.com/security/cve/CVE-2026-33150
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33150.json
- https://github.com/libfuse/libfuse/security/advisories/GHSA-qxv7-xrc2-qmfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33150
- https://bugzilla.redhat.com/show_bug.cgi?id=2449771
- https://github.com/libfuse/libfuse/commit/49fcd891a58f622c098e2ca67d66086f7b213836
