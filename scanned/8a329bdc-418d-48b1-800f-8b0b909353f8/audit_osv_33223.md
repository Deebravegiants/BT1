# [M] nfs/localio: restore creds before releasing pageio data

## Summary
Severity: Medium
Advisory: CVE-2025-39912
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39912
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfs/localio: restore creds before releasing pageio data

Otherwise if the nfsd filecache code releases the nfsd_file
immediately, it can trigger the BUG_ON(cred == current->cred) in
__put_cred() when it puts the nfsd_file->nf_file->f-cred.

## References
- https://git.kernel.org/stable/c/57c1bb02b4fc8eec6eb01736e7fad26dffacf18c
- https://git.kernel.org/stable/c/992203a1fba51b025c60ec0c8b0d9223343dea95
- https://git.kernel.org/stable/c/c250be1d75bf80dc5ab46f0b434b746c1868a1ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39912.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39912
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
