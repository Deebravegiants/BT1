# [H] drm/amdgpu: Fix variable 'mca_funcs' dereferenced before NULL check in 'amdgpu_mca_smu_get_mca_entry()'

## Summary
Severity: High
Advisory: CVE-2024-26672
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26672
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix variable 'mca_funcs' dereferenced before NULL check in 'amdgpu_mca_smu_get_mca_entry()'

Fixes the below:

drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c:377 amdgpu_mca_smu_get_mca_entry() warn: variable dereferenced before check 'mca_funcs' (see line 368)

357 int amdgpu_mca_smu_get_mca_entry(struct amdgpu_device *adev,
				     enum amdgpu_mca_error_type type,
358                                  int idx, struct mca_bank_entry *entry)
359 {
360         const struct amdgpu_mca_smu_funcs *mca_funcs =
						adev->mca.mca_funcs;
361         int count;
362
363         switch (type) {
364         case AMDGPU_MCA_ERROR_TYPE_UE:
365                 count = mca_funcs->max_ue_count;

mca_funcs is dereferenced here.

366                 break;
367         case AMDGPU_MCA_ERROR_TYPE_CE:
368                 count = mca_funcs->max_ce_count;

mca_funcs is dereferenced here.

369                 break;
370         default:
371                 return -EINVAL;
372         }
373
374         if (idx >= count)
375                 return -EINVAL;
376
377         if (mca_funcs && mca_funcs->mca_get_mca_entry)
	        ^^^^^^^^^

Checked too late!

## References
- https://git.kernel.org/stable/c/4f32504a2f85a7b40fe149436881381f48e9c0c0
- https://git.kernel.org/stable/c/7b5d58c07024516c0e81b95e98f37710cf402c53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26672.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26672
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
