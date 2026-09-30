# [C] nvme-tcp: fix UAF when detecting digest errors

## Summary
Severity: Critical
Advisory: CVE-2022-48686
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2022-48686
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.213, >=5.5.0 <5.10.143, >=5.11.0 <5.15.68, >=5.16.0 <5.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-tcp: fix UAF when detecting digest errors

We should also bail from the io_work loop when we set rd_enabled to true,
so we don't attempt to read data from the socket when the TCP stream is
already out-of-sync or corrupted.

## References
- https://git.kernel.org/stable/c/13c80a6c112467bab5e44d090767930555fc17a5
- https://git.kernel.org/stable/c/160f3549a907a50e51a8518678ba2dcf2541abea
- https://git.kernel.org/stable/c/19816a0214684f70b49b25075ff8c402fdd611d3
- https://git.kernel.org/stable/c/5914fa32ef1b7766fea933f9eed94ac5c00aa7ff
- https://git.kernel.org/stable/c/c3eb461aa56e6fa94fb80442ba2586bd223a8886
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48686.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48686
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
