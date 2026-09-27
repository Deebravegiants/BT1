# [H] mm/page_reporting: use system_freezable_wq to fix UAF during suspend

## Summary
Severity: High
Advisory: CVE-2026-74481
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74481
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/page_reporting: use system_freezable_wq to fix UAF during suspend

During PM freeze (e.g.  S3 suspend or S4 hibernation), device drivers like
virtio_balloon reset their underlying virtio devices and delete their
virtqueues via vdev->config->del_vqs().

However, page reporting work (page_reporting_process) was scheduled on the
global system_wq.  Because system_wq lacks the WQ_FREEZABLE flag, the PM
freezer skips it, leaving page_reporting_process active during suspend.

If pages are freed into the buddy allocator while suspending (for example,
when core MM invokes the balloon shrinker during S4 hibernation image
saving), page reporting triggers virtballoon_free_page_report() on deleted
virtqueues, resulting in a Use-After-Free / General Protection Fault:

    [  196.795226] general protection fault, probably for non-canonical address 0xaa1436fe70dae6df: 0000 [#1] SMP NOPTI
    [  196.825967] Workqueue: events page_reporting_process
    [  196.831038] RIP: 0010:virtqueue_add_split+0x233/0x4c0 [virtio_ring]
    [  196.927073] virtballoon_free_page_report+0x3a/0xe0 [virtio_balloon]
    [  196.946943] page_reporting_process+0x370/0x4f0

Fix this by switching page reporting work to system_freezable_wq.  This
ensures that the PM freezer pauses page_reporting_process before device
drivers destroy their reporting virtqueues.  Because the reporting worker
is frozen, memory reclamation/freeing (e.g.  via shrinker execution) can
safely return pages to MM during freeze without triggering unfrozen
reporting work on deleted virtqueues.

This aligns with the driver's existing design. The comment in
virtballoon_freeze() states:
    /*
     * The workqueue is already frozen by the PM core before this
     * function is called.
     */

Testing:
I have verified these fixes using Google’s virtualization infrastructure
by running continuous suspend/resume iterations (40+ cycles) while
churning memory using stress-ng (`stress-ng --vm 4 --vm-bytes 60%
--timeout 1`) to constantly create free pages for the buddy allocator.  We
also set the `page_reporting_order` parameter to 0 to make the page
reporting worker highly sensitive, forcing it to pick up any 4K free
pages.  This confirmed that the UAF crashes are no longer reproducible.

## References
- https://git.kernel.org/stable/c/0b45f6927a14914ff685fe0e6f9d11232a1e03df
- https://git.kernel.org/stable/c/450f35f4d5a682a0796757e52295df58ddb63bc9
- https://git.kernel.org/stable/c/992f270fd808338fbae1f498a5e325e7e2e20368
- https://git.kernel.org/stable/c/a4c60046052777ca1dcc83fe3ece2a5136b301f1
- https://git.kernel.org/stable/c/b11907c905fa08eda925395f0724b7a409870f65
- https://git.kernel.org/stable/c/b2c094e98f8bb823b3ae475f7169fe2091c40c6d
- https://git.kernel.org/stable/c/f978048326570047e8216e81a67f9c71ef2bb1b1
- https://git.kernel.org/stable/c/faf439b5fa7b231120eac4f7a617e0bfd4f6f5c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74481.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74481
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
