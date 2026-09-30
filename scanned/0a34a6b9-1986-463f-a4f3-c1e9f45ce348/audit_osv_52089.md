# [H] CVE-2021-47058

## Summary
Severity: High
Advisory: CVE-2021-47058
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47058
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

regmap: set debugfs_name to NULL after it is freed

There is a upstream commit cffa4b2122f5("regmap:debugfs:
Fix a memory leak when calling regmap_attach_dev") that
adds a if condition when create name for debugfs_name.
With below function invoking logical, debugfs_name is
freed in regmap_debugfs_exit(), but it is not created again
because of the if condition introduced by above commit.
regmap_reinit_cache()
	regmap_debugfs_exit()
	...
	regmap_debugfs_init()
So, set debugfs_name to NULL after it is freed.

## References
- https://git.kernel.org/stable/c/2dc1554d5f0fdaf47cc5bea442b84b9226fea867
- https://git.kernel.org/stable/c/b9e569ae1da3a113b3acee8703c94777fd20938a
- https://git.kernel.org/stable/c/c764e375ae647832de1ee73d43a4bb3ef8a8f43d
- https://git.kernel.org/stable/c/d8897f7b2283a500666c85ef06e820df38ed7b52
- https://git.kernel.org/stable/c/e41a962f82e7afb5b1ee644f48ad0b3aee656268
- https://git.kernel.org/stable/c/eb949f891226c012138ffd9df90d1e509f428ae6
