# [H] drm/amdkfd: Check debug trap enable before write dbg_ev_file

## Summary
Severity: High
Advisory: CVE-2024-46803
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46803
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Check debug trap enable before write dbg_ev_file

In interrupt context, write dbg_ev_file will be run by work queue. It
will cause write dbg_ev_file execution after debug_trap_disable, which
will cause NULL pointer access.
v2: cancel work "debug_event_workarea" before set dbg_ev_file as NULL.

## References
- https://git.kernel.org/stable/c/547033b593063eb85bfdf9b25a5f1b8fd1911be2
- https://git.kernel.org/stable/c/820dcbd38a77bd5fdc4236d521c1c122841227d0
- https://git.kernel.org/stable/c/e6ea3b8fe398915338147fe54dd2db8155fdafd8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46803.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46803
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
