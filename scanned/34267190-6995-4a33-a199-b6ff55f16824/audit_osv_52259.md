# [M] CVE-2021-47253

## Summary
Severity: Medium
Advisory: CVE-2021-47253
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47253
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix potential memory leak in DMUB hw_init

[Why]
On resume we perform DMUB hw_init which allocates memory:
dm_resume->dm_dmub_hw_init->dc_dmub_srv_create->kzalloc
That results in memory leak in suspend/resume scenarios.

[How]
Allocate memory for the DC wrapper to DMUB only if it was not
allocated before.
No need to reallocate it on suspend/resume.

## References
- https://git.kernel.org/stable/c/9e8c2af010463197315fa54a6c17e74988b5259c
- https://git.kernel.org/stable/c/aa000f828e60ac15d6340f606ec4a673966f5b0b
- https://git.kernel.org/stable/c/c5699e2d863f58221044efdc3fa712dd32d55cde
