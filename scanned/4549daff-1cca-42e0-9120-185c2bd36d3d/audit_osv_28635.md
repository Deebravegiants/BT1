# [M] PCI/PM: Drain runtime-idle callbacks before driver removal

## Summary
Severity: Medium
Advisory: CVE-2024-35809
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35809
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI/PM: Drain runtime-idle callbacks before driver removal

A race condition between the .runtime_idle() callback and the .remove()
callback in the rtsx_pcr PCI driver leads to a kernel crash due to an
unhandled page fault [1].

The problem is that rtsx_pci_runtime_idle() is not expected to be running
after pm_runtime_get_sync() has been called, but the latter doesn't really
guarantee that.  It only guarantees that the suspend and resume callbacks
will not be running when it returns.

However, if a .runtime_idle() callback is already running when
pm_runtime_get_sync() is called, the latter will notice that the runtime PM
status of the device is RPM_ACTIVE and it will return right away without
waiting for the former to complete.  In fact, it cannot wait for
.runtime_idle() to complete because it may be called from that callback (it
arguably does not make much sense to do that, but it is not strictly
prohibited).

Thus in general, whoever is providing a .runtime_idle() callback needs
to protect it from running in parallel with whatever code runs after
pm_runtime_get_sync().  [Note that .runtime_idle() will not start after
pm_runtime_get_sync() has returned, but it may continue running then if it
has started earlier.]

One way to address that race condition is to call pm_runtime_barrier()
after pm_runtime_get_sync() (not before it, because a nonzero value of the
runtime PM usage counter is necessary to prevent runtime PM callbacks from
being invoked) to wait for the .runtime_idle() callback to complete should
it be running at that point.  A suitable place for doing that is in
pci_device_remove() which calls pm_runtime_get_sync() before removing the
driver, so it may as well call pm_runtime_barrier() subsequently, which
will prevent the race in question from occurring, not just in the rtsx_pcr
driver, but in any PCI drivers providing .runtime_idle() callbacks.

## References
- https://git.kernel.org/stable/c/47d8aafcfe313511a98f165a54d0adceb34e54b1
- https://git.kernel.org/stable/c/6347348c6aba52dda0b33296684cbb627bdc6970
- https://git.kernel.org/stable/c/7cc94dd36e48879e76ae7a8daea4ff322b7d9674
- https://git.kernel.org/stable/c/900b81caf00c89417172afe0e7e49ac4eb110f4b
- https://git.kernel.org/stable/c/9a87375bb586515c0af63d5dcdcd58ec4acf20a6
- https://git.kernel.org/stable/c/9d5286d4e7f68beab450deddbb6a32edd5ecf4bf
- https://git.kernel.org/stable/c/bbe068b24409ef740657215605284fc7cdddd491
- https://git.kernel.org/stable/c/d534198311c345e4b062c4b88bb609efb8bd91d5
- https://git.kernel.org/stable/c/d86ad8c3e152349454b82f37007ff6ba45f26989
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35809.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35809
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
