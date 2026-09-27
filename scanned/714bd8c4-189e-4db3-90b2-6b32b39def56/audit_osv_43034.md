# [C] netfs: Fix barriering when walking subrequest list

## Summary
Severity: Critical
Advisory: CVE-2026-72355
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72355
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix barriering when walking subrequest list

Fix the barriering used when walking the subrequest list in retry as
there's a possibility of seeing a subreq that's just been added by the
application thread.

## References
- https://git.kernel.org/stable/c/5c6ce05e406520290c1d89da97fb3cd70c09137d
- https://git.kernel.org/stable/c/be47c047250671c9225c0319ca4695be9b391c59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72355.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72355
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
