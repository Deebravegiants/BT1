# [M] scsi: mpi3mr: Fix memory leaks

## Summary
Severity: Medium
Advisory: CVE-2022-49126
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49126
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpi3mr: Fix memory leaks

Fix memory leaks related to operational reply queue's memory segments which
are not getting freed while unloading the driver.

## References
- https://git.kernel.org/stable/c/27fc9e90171ab0a94a411f3fdb3522ef5acb9537
- https://git.kernel.org/stable/c/5d76a88b8536d75ff5362e232097e85946b8aadf
- https://git.kernel.org/stable/c/71c7ac65a084ae7d387c3c1d02d59edfdecb009f
- https://git.kernel.org/stable/c/d44b5fefb22e139408ae12b864da1ecb9ad9d1d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49126.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49126
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
