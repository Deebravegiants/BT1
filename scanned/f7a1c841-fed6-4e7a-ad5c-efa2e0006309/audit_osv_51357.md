# [M] CVE-2021-29649

## Summary
Severity: Medium
Advisory: CVE-2021-29649
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-30
Source: https://osv.dev/vulnerability/CVE-2021-29649
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.11.11. The user mode driver (UMD) has a copy_process() memory leak, related to a lack of cleanup steps in kernel/usermode_driver.c and kernel/bpf/preload/bpf_preload_kern.c, aka CID-f60a85cad677.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RZGMUP6QEHJJEKPMLKOSPWYMW7PXFC2M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VTADK5ELGTATGW2RK3K5MBJ2WGYCPZCM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WKRNELXLVFDY6Y5XDMWLIH3VKIMQXLLR/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.11
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f60a85cad677c4f9bb4cadd764f1d106c38c7cf8
