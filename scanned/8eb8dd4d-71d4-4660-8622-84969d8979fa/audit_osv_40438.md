# [H] accel/ivpu: Fix signed integer truncation in IPC receive

## Summary
Severity: High
Advisory: CVE-2026-53202
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53202
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Fix signed integer truncation in IPC receive

Fix potential buffer overflow where firmware-supplied data_size is cast
to signed int before being used in min_t(). Large unsigned values
(>= 0x80000000) become negative, causing unsigned wraparound and
oversized memcpy operations that can overflow the stack buffer.

Change min_t(int, ...) to min() as both values are unsigned and can be
handled by min() without explicit cast.

## References
- https://git.kernel.org/stable/c/2821bf2b79e47f87e1dbdd9d25c78240965a97d6
- https://git.kernel.org/stable/c/45cb105b8642c65e9be286f7058e92314efe7ea3
- https://git.kernel.org/stable/c/4788556d4dd9d717037e385de178974e9649231d
- https://git.kernel.org/stable/c/d9faef564438d1e4579c692c046603e7ada7bdf4
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53202.json
- https://access.redhat.com/errata/RHSA-2026:54343
- https://access.redhat.com/errata/RHSA-2026:54443
- https://access.redhat.com/security/cve/CVE-2026-53202
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53202.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53202
- https://bugzilla.redhat.com/show_bug.cgi?id=2492823
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
