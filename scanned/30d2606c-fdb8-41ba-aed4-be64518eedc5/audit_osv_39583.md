# [H] batman-adv: stop tp_meter sessions during mesh teardown

## Summary
Severity: High
Advisory: CVE-2026-46208
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46208
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: stop tp_meter sessions during mesh teardown

TP meter sessions remain linked on bat_priv->tp_list after the netlink
request has already finished. When the mesh interface is removed,
batadv_mesh_free() currently tears down the mesh without first draining
these sessions.

A running sender thread or a late incoming tp_meter packet can then keep
processing against a mesh instance which is already shutting down.
Synchronize tp_meter with the mesh lifetime by stopping all active
sessions from batadv_mesh_free() and waiting for sender threads to exit
before teardown continues.

## References
- https://git.kernel.org/stable/c/03660dab86f93319178a24667f6998526dc4355d
- https://git.kernel.org/stable/c/268078acae72daa12b17b2b299701cb9924e469a
- https://git.kernel.org/stable/c/26dfeee8db81354bfdade155f27f9e16510ad196
- https://git.kernel.org/stable/c/3d3cf6a7314aca4df0a6dde28ce784a2a30d0166
- https://git.kernel.org/stable/c/58943b7ea356294749dae3e75b96c0ee292c00be
- https://git.kernel.org/stable/c/5e7d0ac936354c36810e74ac3056b334ed1f4058
- https://git.kernel.org/stable/c/79bc0eaeef2c5797317bf2da8e3159a74d62ec47
- https://git.kernel.org/stable/c/8634c1dbd73adb74d40533ebb7e914efb82e71fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46208
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
