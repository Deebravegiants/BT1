# [M] CVE-2022-38457

## Summary
Severity: Medium
Advisory: CVE-2022-38457
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-09
Source: https://osv.dev/vulnerability/CVE-2022-38457
Type: osv

## Details
A use-after-free(UAF) vulnerability was found in function 'vmw_cmd_res_check' in drivers/gpu/vmxgfx/vmxgfx_execbuf.c in Linux kernel's vmwgfx driver with device file '/dev/dri/renderD128 (or Dxxx)'. This flaw allows a local attacker with a user account on the system to gain privilege, causing a denial of service(DoS).

## References
- https://bugzilla.openanolis.cn/show_bug.cgi?id=2074
