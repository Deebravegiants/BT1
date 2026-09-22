# [H] Bluetooth: l2cap: Add missing chan lock in l2cap_ecred_reconf_rsp

## Summary
Severity: High
Advisory: CVE-2026-53071
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53071
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: l2cap: Add missing chan lock in l2cap_ecred_reconf_rsp

l2cap_ecred_reconf_rsp() calls l2cap_chan_del() without holding
l2cap_chan_lock(). Every other l2cap_chan_del() caller in the file
acquires the lock first. A remote BLE device can send a crafted
L2CAP ECRED reconfiguration response to corrupt the channel list
while another thread is iterating it.

Add l2cap_chan_hold() and l2cap_chan_lock() before l2cap_chan_del(),
and l2cap_chan_unlock() and l2cap_chan_put() after, matching the
pattern used in l2cap_ecred_conn_rsp() and l2cap_conn_del().

## References
- https://git.kernel.org/stable/c/0ccd75c51f620374086f359e906917676e699a1c
- https://git.kernel.org/stable/c/330b20ec97916961ee0e6c29c06bc0fa7c96e64c
- https://git.kernel.org/stable/c/42776497cdbc9a665b384a6dcb85f0d4bd927eab
- https://git.kernel.org/stable/c/5501d055a1ce3c747141e3955ba8cf034d193f3e
- https://git.kernel.org/stable/c/77a853aec710b2fdf41fa298ea3cbc9a4358f917
- https://git.kernel.org/stable/c/96dca51715d86559ed6ed8028e5445cecb80f3ae
- https://git.kernel.org/stable/c/dc89961b76f12aff47124c1df4bdb32a080f4d0c
- https://git.kernel.org/stable/c/fe1188abdae9b7a8199dcdfcf9244d5e5d61eb14
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53071.json
- https://access.redhat.com/errata/RHSA-2026:42550
- https://access.redhat.com/errata/RHSA-2026:42552
- https://access.redhat.com/errata/RHSA-2026:42919
- https://access.redhat.com/errata/RHSA-2026:43307
- https://access.redhat.com/errata/RHSA-2026:65710
- https://access.redhat.com/errata/RHSA-2026:65711
- https://access.redhat.com/security/cve/CVE-2026-53071
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53071.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53071
- https://bugzilla.redhat.com/show_bug.cgi?id=2492458
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
