# [H] accel/amdxdna: Fix use-after-free of mm_struct in job scheduler

## Summary
Severity: High
Advisory: CVE-2026-68380
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68380
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Fix use-after-free of mm_struct in job scheduler

amdxdna_cmd_submit() stores current->mm in job->mm without holding any
reference. aie2_sched_job_run() later access job->mm from the DRM
scheduler worker thread. With only a raw pointer and no structural
reference, the mm_struct can be freed before the scheduler runs the job.

Fix this by calling mmgrab() to hold a structural mm_count reference for
the lifetime of the job, paired with mmdrop() in every cleanup path.

## References
- https://git.kernel.org/stable/c/6875ee2bef48f5d9f045d81a8a4d68893f768a8a
- https://git.kernel.org/stable/c/e8fadbffc19a233d1eedebfb8df0f522d1388280
- https://git.kernel.org/stable/c/faebb7ba1ac65fa5810b640df02ce04e509fdc11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68380.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68380
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
