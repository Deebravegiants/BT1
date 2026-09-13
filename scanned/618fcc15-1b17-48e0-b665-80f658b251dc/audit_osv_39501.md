# [H] accel/amdxdna: Stop job scheduling across aie2_release_resource()

## Summary
Severity: High
Advisory: CVE-2026-45980
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45980
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Stop job scheduling across aie2_release_resource()

Running jobs on a hardware context while it is in the process of
releasing resources can lead to use-after-free and crashes.

Fix this by stopping job scheduling before calling
aie2_release_resource() and restarting it after the release completes.
Additionally, aie2_sched_job_run() now checks whether the hardware
context is still active.

## References
- https://git.kernel.org/stable/c/688c3ff079b10e4600f040944430d3d4ff448a15
- https://git.kernel.org/stable/c/b79d31dce49b50c79620389b3639280802a86960
- https://git.kernel.org/stable/c/f1370241fe8045702bc9d0812b996791f0500f1b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45980.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45980
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
