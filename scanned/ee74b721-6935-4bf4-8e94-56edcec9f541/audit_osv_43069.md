# [H] net: dsa: mxl862xx: fix use-after-free of DSA ports in crc_err_work

## Summary
Severity: High
Advisory: CVE-2026-72411
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72411
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: mxl862xx: fix use-after-free of DSA ports in crc_err_work

Upon an MDIO CRC error mxl862xx_crc_err_work_fn() walks the DSA ports
and closes the CPU port conduits:

	dsa_switch_for_each_cpu_port(dp, priv->ds)
		dev_close(dp->conduit);

mxl862xx_remove() unregisters the switch before cancelling this work:

	set_bit(MXL862XX_FLAG_WORK_STOPPED, &priv->flags);
	cancel_delayed_work_sync(&priv->stats_work);
	dsa_unregister_switch(ds);
	mxl862xx_host_shutdown(priv);

dsa_unregister_switch() frees the dsa_port objects. If a CRC error
schedules the work during teardown it can run after the ports have been
freed and dereference freed memory.

Guard the port walk with MXL862XX_FLAG_WORK_STOPPED, which is already set
before dsa_unregister_switch(). DSA tears the ports down under
rtnl_lock(), so checking the flag under rtnl_lock() means the work either
runs before teardown and sees valid ports, or runs afterwards, observes
the flag and skips the walk. This mirrors the host_flood_work handler,
which skips torn-down ports under rtnl_lock().

## References
- https://git.kernel.org/stable/c/bcb3b8314611ed9cb4ff4bff484ef9b154fd1b83
- https://git.kernel.org/stable/c/cf52622fbc274eb4ca9a2066b258da2ae3dc7406
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72411.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72411
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
