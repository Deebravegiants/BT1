# [H] drm/v3d: Ensure job pointer is set to NULL after job completion

## Summary
Severity: High
Advisory: CVE-2025-21697
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-21697
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/v3d: Ensure job pointer is set to NULL after job completion

After a job completes, the corresponding pointer in the device must
be set to NULL. Failing to do so triggers a warning when unloading
the driver, as it appears the job is still active. To prevent this,
assign the job pointer to NULL after completing the job, indicating
the job has finished.

## References
- https://git.kernel.org/stable/c/14e0a874488e79086340ba8e2d238cb9596b68a8
- https://git.kernel.org/stable/c/1bd6303d08c85072ce40ac01a767ab67195105bd
- https://git.kernel.org/stable/c/2a1c88f7ca5c12dff6fa6787492ac910bb9e4407
- https://git.kernel.org/stable/c/63195bae1cbf78f1d392b1bc9ae4b03c82d0ebf3
- https://git.kernel.org/stable/c/a34050f70e7955a359874dff1a912a748724a140
- https://git.kernel.org/stable/c/b22467b1ae104073dcb11aa78562a331cd7fb0e0
- https://git.kernel.org/stable/c/e4b5ccd392b92300a2b341705cc4805681094e49
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21697.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
