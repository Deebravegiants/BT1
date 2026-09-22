# [M] CVE-2021-47431

## Summary
Severity: Medium
Advisory: CVE-2021-47431
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47431
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix gart.bo pin_count leak

gmc_v{9,10}_0_gart_disable() isn't called matched with
correspoding gart_enbale function in SRIOV case. This will
lead to gart.bo pin_count leak on driver unload.

## References
- https://git.kernel.org/stable/c/18d1c5ea3798ba42cfa0f8b2264d873463facb03
- https://git.kernel.org/stable/c/621ddffb70db824eabd63d18ac635180fe9500f9
- https://git.kernel.org/stable/c/66805763a97f8f7bdf742fc0851d85c02ed9411f
- https://git.kernel.org/stable/c/83d857d6b0967b6709cd38750c3ce2ed8ced1a95
