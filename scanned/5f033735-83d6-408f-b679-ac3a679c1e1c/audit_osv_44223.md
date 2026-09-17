# [H] veth: fix NAPI leak in XDP enable error path

## Summary
Severity: High
Advisory: CVE-2026-80613
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80613
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

veth: fix NAPI leak in XDP enable error path

During XDP enablement in veth, if xdp_rxq_info_reg() or
xdp_rxq_info_reg_mem_model() fails, the driver rolls back the changes.

However, the rollback loop:
	for (i--; i >= start; i--) {

decrements the loop index 'i' before the first iteration. This
correctly skips unregistering the rxq for the failed index 'i' (as
registration failed or was already cleaned up), but it also
erroneously skips calling netif_napi_deli() for rq[i].xdp_napi.

Since netif_napi_add() was already called for index 'i', this leaves
a dangling napi_struct in the device's napi_list. When the veth
device is later destroyed, the freed queue memory (which contains the
leaked NAPI structure) can be reused.

The subsequent device teardown iterates the NAPI list and
corrupts the reallocated memory, leading to UAF.

Fix this by explicitly deleting the NAPI association for the failed
index 'i' before rolling back the successfully configured queues.

## References
- https://git.kernel.org/stable/c/4559770b2a241344d762719e674241fcc8528f02
- https://git.kernel.org/stable/c/4bd2e5dbe62334aae1182d0f0d260f334a49d739
- https://git.kernel.org/stable/c/6739027cb72da26890edd424c77080d187b2a92e
- https://git.kernel.org/stable/c/83090f5e7b54721d71875a6c224d2490b9e73050
- https://git.kernel.org/stable/c/a9e6707322ef215d39d4655b176c094f45f0ab52
- https://git.kernel.org/stable/c/d3eb258ad398cc9402bab3a5e730cd7c5b34efad
- https://git.kernel.org/stable/c/fc51373345e7e6ea73da2650cb497309c50b077a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80613.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80613
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
