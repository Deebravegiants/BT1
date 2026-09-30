# [H] rpmsg: char: Fix race between the release of rpmsg_ctrldev and cdev

## Summary
Severity: High
Advisory: CVE-2022-48759
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48759
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.14.265, >=4.15.0 <4.19.228, >=4.20.0 <5.4.176, >=5.5.0 <5.10.96, >=5.11.0 <5.15.19, >=5.16.0 <5.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rpmsg: char: Fix race between the release of rpmsg_ctrldev and cdev

struct rpmsg_ctrldev contains a struct cdev. The current code frees
the rpmsg_ctrldev struct in rpmsg_ctrldev_release_device(), but the
cdev is a managed object, therefore its release is not predictable
and the rpmsg_ctrldev could be freed before the cdev is entirely
released, as in the backtrace below.

[   93.625603] ODEBUG: free active (active state 0) object type: timer_list hint: delayed_work_timer_fn+0x0/0x7c
[   93.636115] WARNING: CPU: 0 PID: 12 at lib/debugobjects.c:488 debug_print_object+0x13c/0x1b0
[   93.644799] Modules linked in: veth xt_cgroup xt_MASQUERADE rfcomm algif_hash algif_skcipher af_alg uinput ip6table_nat fuse uvcvideo videobuf2_vmalloc venus_enc venus_dec videobuf2_dma_contig hci_uart btandroid btqca snd_soc_rt5682_i2c bluetooth qcom_spmi_temp_alarm snd_soc_rt5682v
[   93.715175] CPU: 0 PID: 12 Comm: kworker/0:1 Tainted: G    B             5.4.163-lockdep #26
[   93.723855] Hardware name: Google Lazor (rev3 - 8) with LTE (DT)
[   93.730055] Workqueue: events kobject_delayed_cleanup
[   93.735271] pstate: 60c00009 (nZCv daif +PAN +UAO)
[   93.740216] pc : debug_print_object+0x13c/0x1b0
[   93.744890] lr : debug_print_object+0x13c/0x1b0
[   93.749555] sp : ffffffacf5bc7940
[   93.752978] x29: ffffffacf5bc7940 x28: dfffffd000000000
[   93.758448] x27: ffffffacdb11a800 x26: dfffffd000000000
[   93.763916] x25: ffffffd0734f856c x24: dfffffd000000000
[   93.769389] x23: 0000000000000000 x22: ffffffd0733c35b0
[   93.774860] x21: ffffffd0751994a0 x20: ffffffd075ec27c0
[   93.780338] x19: ffffffd075199100 x18: 00000000000276e0
[   93.785814] x17: 0000000000000000 x16: dfffffd000000000
[   93.791291] x15: ffffffffffffffff x14: 6e6968207473696c
[   93.796768] x13: 0000000000000000 x12: ffffffd075e2b000
[   93.802244] x11: 0000000000000001 x10: 0000000000000000
[   93.807723] x9 : d13400dff1921900 x8 : d13400dff1921900
[   93.813200] x7 : 0000000000000000 x6 : 0000000000000000
[   93.818676] x5 : 0000000000000080 x4 : 0000000000000000
[   93.824152] x3 : ffffffd0732a0fa4 x2 : 0000000000000001
[   93.829628] x1 : ffffffacf5bc7580 x0 : 0000000000000061
[   93.835104] Call trace:
[   93.837644]  debug_print_object+0x13c/0x1b0
[   93.841963]  __debug_check_no_obj_freed+0x25c/0x3c0
[   93.846987]  debug_check_no_obj_freed+0x18/0x20
[   93.851669]  slab_free_freelist_hook+0xbc/0x1e4
[   93.856346]  kfree+0xfc/0x2f4
[   93.859416]  rpmsg_ctrldev_release_device+0x78/0xb8
[   93.864445]  device_release+0x84/0x168
[   93.868310]  kobject_cleanup+0x12c/0x298
[   93.872356]  kobject_delayed_cleanup+0x10/0x18
[   93.876948]  process_one_work+0x578/0x92c
[   93.881086]  worker_thread+0x804/0xcf8
[   93.884963]  kthread+0x2a8/0x314
[   93.888303]  ret_from_fork+0x10/0x18

The cdev_device_add/del() API was created to address this issue (see
commit '233ed09d7fda ("chardev: add helper function to register char
devs with a struct device")'), use it instead of cdev add/del().

## References
- https://git.kernel.org/stable/c/1dbb206730f3e5ce90014ad569ddf8167ec4124a
- https://git.kernel.org/stable/c/70cb4295ec806b663665e1d2ed15caab6159880e
- https://git.kernel.org/stable/c/74d85e9fbc7022a4011102c7474a9c7aeb704a35
- https://git.kernel.org/stable/c/85aba11a8ea92a8eef2de95ebbe063086fd62d9c
- https://git.kernel.org/stable/c/b7fb2dad571d1e21173c06cef0bced77b323990a
- https://git.kernel.org/stable/c/d6cdc6ae542845d4d0ac8b6d99362bde7042a3c7
- https://git.kernel.org/stable/c/da27b834c1e0222e149e06caddf7718478086d1b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48759.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48759
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
