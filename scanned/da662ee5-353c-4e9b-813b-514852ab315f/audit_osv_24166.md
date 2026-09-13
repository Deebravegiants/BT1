# [M] drm/vkms: Fix null-ptr-deref in vkms_release()

## Summary
Severity: Medium
Advisory: CVE-2022-50369
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50369
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vkms: Fix null-ptr-deref in vkms_release()

A null-ptr-deref is triggered when it tries to destroy the workqueue in
vkms->output.composer_workq in vkms_release().

 KASAN: null-ptr-deref in range [0x0000000000000118-0x000000000000011f]
 CPU: 5 PID: 17193 Comm: modprobe Not tainted 6.0.0-11331-gd465bff130bf #24
 RIP: 0010:destroy_workqueue+0x2f/0x710
 ...
 Call Trace:
  <TASK>
  ? vkms_config_debugfs_init+0x50/0x50 [vkms]
  __devm_drm_dev_alloc+0x15a/0x1c0 [drm]
  vkms_init+0x245/0x1000 [vkms]
  do_one_initcall+0xd0/0x4f0
  do_init_module+0x1a4/0x680
  load_module+0x6249/0x7110
  __do_sys_finit_module+0x140/0x200
  do_syscall_64+0x35/0x80
  entry_SYSCALL_64_after_hwframe+0x46/0xb0

The reason is that an OOM happened which triggers the destroy of the
workqueue, however, the workqueue is alloced in the later process,
thus a null-ptr-deref happened. A simple call graph is shown as below:

 vkms_init()
  vkms_create()
    devm_drm_dev_alloc()
      __devm_drm_dev_alloc()
        devm_drm_dev_init()
          devm_add_action_or_reset()
            devm_add_action() # an error happened
            devm_drm_dev_init_release()
              drm_dev_put()
                kref_put()
                  drm_dev_release()
                    vkms_release()
                      destroy_workqueue() # null-ptr-deref happened
    vkms_modeset_init()
      vkms_output_init()
        vkms_crtc_init() # where the workqueue get allocated

Fix this by checking if composer_workq is NULL before passing it to
the destroy_workqueue() in vkms_release().

## References
- https://git.kernel.org/stable/c/0b8f390e2251191f1b179cc87f65d54c96565f0d
- https://git.kernel.org/stable/c/1f9836f95271e7acf016667eee0aeae3386f9645
- https://git.kernel.org/stable/c/2fe2a8f40c21161ffe7653cc234e7934db5b7cc5
- https://git.kernel.org/stable/c/57031c474c3a920ea73afeb5dc352e537f5793ee
- https://git.kernel.org/stable/c/596f1ba3987e601e31a5abf1f75ce1d2635aceac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50369.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50369
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
