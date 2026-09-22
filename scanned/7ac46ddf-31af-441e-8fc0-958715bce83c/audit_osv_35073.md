# [H] drm/xe/guc: Synchronize Dead CT worker with unbind

## Summary
Severity: High
Advisory: CVE-2025-68207
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68207
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/guc: Synchronize Dead CT worker with unbind

Cancel and wait for any Dead CT worker to complete before continuing
with device unbinding. Else the worker will end up using resources freed
by the undind operation.

(cherry picked from commit 492671339114e376aaa38626d637a2751cdef263)

## References
- https://git.kernel.org/stable/c/35959ab7d16b618616edf6df882a4533d2efe193
- https://git.kernel.org/stable/c/95af8f4fdce8349a5fe75264007f1af2aa1082ea
- https://git.kernel.org/stable/c/ce6ccf8e881a919bf902174ac879f80c97669498
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68207.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68207
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
