# [H] CVE-2022-3541

## Summary
Severity: High
Advisory: CVE-2022-3541
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3541
Type: osv

## Details
A vulnerability classified as critical has been found in Linux Kernel. This affects the function spl2sw_nvmem_get_mac_address of the file drivers/net/ethernet/sunplus/spl2sw_driver.c of the component BPF. The manipulation leads to use after free. It is recommended to apply a patch to fix this issue. The identifier VDB-211041 was assigned to this vulnerability.

## References
- https://vuldb.com/?id.211041
- https://security.netapp.com/advisory/ntap-20221228-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=12aece8b01507a2d357a1861f470e83621fbb6f2
