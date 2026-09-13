# [H] Bluetooth: serialize accept_q access

## Summary
Severity: High
Advisory: CVE-2026-52918
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52918
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: serialize accept_q access

bt_sock_poll() walks the accept queue without synchronization, while
child teardown can unlink the same socket and drop its last reference.
The unsynchronized accept queue walk has existed since the initial
Bluetooth import.

Protect accept_q with a dedicated lock for queue updates and polling.
Also rework bt_accept_dequeue() to take temporary child references under
the queue lock before dropping it and locking the child socket.

## References
- https://git.kernel.org/stable/c/41c8c1c7923e86e0eb59cfb4279349112756a336
- https://git.kernel.org/stable/c/4ec17782fd186f901a7329605d11048b085b945a
- https://git.kernel.org/stable/c/85f8674cae82053f1e6bab295f6a8422cca14db5
- https://git.kernel.org/stable/c/8b4c412e001b0c670eb937beab491af974da55b3
- https://git.kernel.org/stable/c/a218bf69eb51fefe59a3976fa8925261141f681c
- https://git.kernel.org/stable/c/be43e6b4043113c3b3cf887c3c8350f67140274c
- https://git.kernel.org/stable/c/d9ce4de05df2385c19e2c7d12f529144e1a44af1
- https://git.kernel.org/stable/c/e83f5e24da741fa9405aeeff00b08c5ee7c37b88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52918.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52918
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
