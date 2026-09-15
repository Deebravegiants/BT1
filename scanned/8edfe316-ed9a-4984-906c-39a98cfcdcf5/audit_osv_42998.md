# [H] net: atm: reject out-of-range traffic classes in QoS validation

## Summary
Severity: High
Advisory: CVE-2026-72297
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72297
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: atm: reject out-of-range traffic classes in QoS validation

Reject ATM traffic classes above ATM_ANYCLASS in check_tp().
SO_ATMQOS stores the supplied QoS after check_qos() succeeds, so
accepting larger values leaves invalid traffic_class values in
vcc->qos.

That bad state later reaches pvc_info(), which indexes class_name[]
with vcc->qos.{rx,tp}.traffic_class. Values above ATM_ANYCLASS cause
an out-of-bounds read when /proc/net/atm/pvc is read.

Tighten the existing QoS validation so invalid traffic_class values
are rejected at the point where user supplied QoS is accepted.

## References
- https://git.kernel.org/stable/c/15444b57fdc6fc3f3e22a87f791ae5be81e6ecf5
- https://git.kernel.org/stable/c/1a6dda72455b399ce9c1a12695471dc4d5c61add
- https://git.kernel.org/stable/c/2b3e241729e87afed13ac0f666472d5d6ca42e87
- https://git.kernel.org/stable/c/367acd288bc6255e247cb1a1efbf5c6567cab423
- https://git.kernel.org/stable/c/513f820b3f0cf4462e17d84c39ed3948d061a6ea
- https://git.kernel.org/stable/c/806b7b6edc8446e8b94b706807a7090a14d47b5c
- https://git.kernel.org/stable/c/cdf19f380e46192e7084be559638aab1f6ed86a2
- https://git.kernel.org/stable/c/e62adb157c2eaad9ad4867ec6cd9af5b9a51b1c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72297.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72297
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
