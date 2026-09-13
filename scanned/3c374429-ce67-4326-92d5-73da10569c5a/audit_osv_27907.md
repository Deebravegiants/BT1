# [C] scsi: target: pscsi: Fix bio_put() for error case

## Summary
Severity: Critical
Advisory: CVE-2024-26760
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26760
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: pscsi: Fix bio_put() for error case

As of commit 066ff571011d ("block: turn bio_kmalloc into a simple kmalloc
wrapper"), a bio allocated by bio_kmalloc() must be freed by bio_uninit()
and kfree(). That is not done properly for the error case, hitting WARN and
NULL pointer dereference in bio_free().

## References
- https://git.kernel.org/stable/c/1cfe9489fb563e9a0c9cdc5ca68257a44428c2ec
- https://git.kernel.org/stable/c/4ebc079f0c7dcda1270843ab0f38ab4edb8f7921
- https://git.kernel.org/stable/c/de959094eb2197636f7c803af0943cb9d3b35804
- https://git.kernel.org/stable/c/f49b20fd0134da84a6bd8108f9e73c077b7d6231
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26760.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26760
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
