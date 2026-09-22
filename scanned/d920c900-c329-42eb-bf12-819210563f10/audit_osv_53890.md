# [M] CVE-2023-31081

## Summary
Severity: Medium
Advisory: CVE-2023-31081
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-31081
Type: osv

## Details
An issue was discovered in drivers/media/test-drivers/vidtv/vidtv_bridge.c in the Linux kernel 6.2. There is a NULL pointer dereference in vidtv_mux_stop_thread. In vidtv_stop_streaming, after dvb->mux=NULL occurs, it executes vidtv_mux_stop_thread(dvb->mux).

## References
- https://lore.kernel.org/all/CA+UBctDXyiosaiR7YNKCs8k0aWu4gU+YutRcnC+TDJkXpHjQag%40mail.gmail.com/
- https://security.netapp.com/advisory/ntap-20230929-0003/
- https://bugzilla.suse.com/show_bug.cgi?id=1210782
