# [H] drm/amdgpu: change vm->task_info handling

## Summary
Severity: High
Advisory: CVE-2024-41008
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2024-41008
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: change vm->task_info handling

This patch changes the handling and lifecycle of vm->task_info object.
The major changes are:
- vm->task_info is a dynamically allocated ptr now, and its uasge is
  reference counted.
- introducing two new helper funcs for task_info lifecycle management
    - amdgpu_vm_get_task_info: reference counts up task_info before
      returning this info
    - amdgpu_vm_put_task_info: reference counts down task_info
- last put to task_info() frees task_info from the vm.

This patch also does logistical changes required for existing usage
of vm->task_info.

V2: Do not block all the prints when task_info not found (Felix)

V3: Fixed review comments from Felix
   - Fix wrong indentation
   - No debug message for -ENOMEM
   - Add NULL check for task_info
   - Do not duplicate the debug messages (ti vs no ti)
   - Get first reference of task_info in vm_init(), put last
     in vm_fini()

V4: Fixed review comments from Felix
   - fix double reference increment in create_task_info
   - change amdgpu_vm_get_task_info_pasid
   - additional changes in amdgpu_gem.c while porting

## References
- https://git.kernel.org/stable/c/b8f67b9ddf4f8fe6dd536590712b5912ad78f99c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41008.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41008
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
