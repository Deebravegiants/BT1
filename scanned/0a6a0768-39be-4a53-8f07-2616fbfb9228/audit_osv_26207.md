# [M] nvme-fc: Prevent null pointer dereference in nvme_fc_io_getuuid()

## Summary
Severity: Medium
Advisory: CVE-2023-52508
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52508
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-fc: Prevent null pointer dereference in nvme_fc_io_getuuid()

The nvme_fc_fcp_op structure describing an AEN operation is initialized with a
null request structure pointer. An FC LLDD may make a call to
nvme_fc_io_getuuid passing a pointer to an nvmefc_fcp_req for an AEN operation.

Add validation of the request structure pointer before dereference.

## References
- https://git.kernel.org/stable/c/8ae5b3a685dc59a8cf7ccfe0e850999ba9727a3c
- https://git.kernel.org/stable/c/be90c9e29dd59b7d19a73297a1590ff3ec1d22ea
- https://git.kernel.org/stable/c/dd46b3ac7322baf3772b33b29726e94f98289db7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52508.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52508
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
