# [H] CVE-2019-18810

## Summary
Severity: High
Advisory: CVE-2019-18810
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18810
Type: osv

## Details
A memory leak in the komeda_wb_connector_add() function in drivers/gpu/drm/arm/display/komeda/komeda_wb_connector.c in the Linux kernel before 5.3.8 allows attackers to cause a denial of service (memory consumption) by triggering drm_writeback_connector_init() failures, aka CID-a0ecd6fdbf5d.

## References
- https://usn.ubuntu.com/4208-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.8
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a0ecd6fdbf5d648123a7315c695fb6850d702835
