# [H] scsi: target: Fix WRITE_SAME No Data Buffer crash

## Summary
Severity: High
Advisory: CVE-2022-21546
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2022-21546
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: Fix WRITE_SAME No Data Buffer crash

In newer version of the SBC specs, we have a NDOB bit that indicates there
is no data buffer that gets written out. If this bit is set using commands
like "sg_write_same --ndob" we will crash in target_core_iblock/file's
execute_write_same handlers when we go to access the se_cmd->t_data_sg
because its NULL.

This patch adds a check for the NDOB bit in the common WRITE SAME code
because we don't support it. And, it adds a check for zero SG elements in
each handler in case the initiator tries to send a normal WRITE SAME with
no data buffer.

## References
- https://git.kernel.org/stable/c/4226622647e3e5ac06d3ebc1605b917446157510
- https://git.kernel.org/stable/c/54e57be2573cf0b8bf650375fd8752987b6c3d3b
- https://git.kernel.org/stable/c/ccd3f449052449a917a3e577d8ba0368f43b8f29
- https://git.kernel.org/stable/c/d8e6a27e9238dd294d6f2f401655f300dca20899
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21546.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21546
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
