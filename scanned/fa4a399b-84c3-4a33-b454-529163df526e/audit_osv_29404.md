# [C] RDMA/iwcm: Fix a use-after-free related to destroying CM IDs

## Summary
Severity: Critical
Advisory: CVE-2024-42285
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42285
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/iwcm: Fix a use-after-free related to destroying CM IDs

iw_conn_req_handler() associates a new struct rdma_id_private (conn_id) with
an existing struct iw_cm_id (cm_id) as follows:

        conn_id->cm_id.iw = cm_id;
        cm_id->context = conn_id;
        cm_id->cm_handler = cma_iw_handler;

rdma_destroy_id() frees both the cm_id and the struct rdma_id_private. Make
sure that cm_work_handler() does not trigger a use-after-free by only
freeing of the struct rdma_id_private after all pending work has finished.

## References
- https://git.kernel.org/stable/c/557d035fe88d78dd51664f4dc0e1896c04c97cf6
- https://git.kernel.org/stable/c/7f25f296fc9bd0435be14e89bf657cd615a23574
- https://git.kernel.org/stable/c/94ee7ff99b87435ec63211f632918dc7f44dac79
- https://git.kernel.org/stable/c/aee2424246f9f1dadc33faa78990c1e2eb7826e4
- https://git.kernel.org/stable/c/d91d253c87fd1efece521ff2612078a35af673c6
- https://git.kernel.org/stable/c/dc8074b8901caabb97c2d353abd6b4e7fa5a59a5
- https://git.kernel.org/stable/c/ee39384ee787e86e9db4efb843818ef0ea9cb8ae
- https://git.kernel.org/stable/c/ff5bbbdee08287d75d72e65b72a2b76d9637892a
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42285.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42285
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
