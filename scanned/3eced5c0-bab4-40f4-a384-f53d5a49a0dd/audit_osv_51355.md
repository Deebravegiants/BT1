# [M] CVE-2021-29646

## Summary
Severity: Medium
Advisory: CVE-2021-29646
Aliases: A-184622243, PUB-A-184622243
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-30
Source: https://osv.dev/vulnerability/CVE-2021-29646
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.11.11. tipc_nl_retrieve_key in net/tipc/node.c does not properly validate certain data sizes, aka CID-0217ed2848e8.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RZGMUP6QEHJJEKPMLKOSPWYMW7PXFC2M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VTADK5ELGTATGW2RK3K5MBJ2WGYCPZCM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WKRNELXLVFDY6Y5XDMWLIH3VKIMQXLLR/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.11
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=0217ed2848e8538bcf9172d97ed2eeb4a26041bb
