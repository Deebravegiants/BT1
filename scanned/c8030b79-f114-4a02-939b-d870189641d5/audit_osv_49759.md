# [H] CVE-2019-18807

## Summary
Severity: High
Advisory: CVE-2019-18807
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18807
Type: osv

## Details
Two memory leaks in the sja1105_static_config_upload() function in drivers/net/dsa/sja1105/sja1105_spi.c in the Linux kernel before 5.3.5 allow attackers to cause a denial of service (memory consumption) by triggering static_config_buf_prepare_for_upload() or sja1105_inhibit_tx() failures, aka CID-68501df92d11.

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.5
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=68501df92d116b760777a2cfda314789f926476f
