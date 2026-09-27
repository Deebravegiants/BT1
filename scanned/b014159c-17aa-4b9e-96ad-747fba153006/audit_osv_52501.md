# [M] CVE-2021-47516

## Summary
Severity: Medium
Advisory: CVE-2021-47516
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47516
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfp: Fix memory leak in nfp_cpp_area_cache_add()

In line 800 (#1), nfp_cpp_area_alloc() allocates and initializes a
CPP area structure. But in line 807 (#2), when the cache is allocated
failed, this CPP area structure is not freed, which will result in
memory leak.

We can fix it by freeing the CPP area when the cache is allocated
failed (#2).

792 int nfp_cpp_area_cache_add(struct nfp_cpp *cpp, size_t size)
793 {
794 	struct nfp_cpp_area_cache *cache;
795 	struct nfp_cpp_area *area;

800	area = nfp_cpp_area_alloc(cpp, NFP_CPP_ID(7, NFP_CPP_ACTION_RW, 0),
801 				  0, size);
	// #1: allocates and initializes

802 	if (!area)
803 		return -ENOMEM;

805 	cache = kzalloc(sizeof(*cache), GFP_KERNEL);
806 	if (!cache)
807 		return -ENOMEM; // #2: missing free

817	return 0;
818 }

## References
- https://git.kernel.org/stable/c/2e0e072e62fdaf7816220af08e05c020f0fcb77a
- https://git.kernel.org/stable/c/3e93abcdcec0436fbf0b6a88ae806902426895a2
- https://git.kernel.org/stable/c/484069b5de9d223cc1c64c6f80389a99cfef51f1
- https://git.kernel.org/stable/c/c56c96303e9289cc34716b1179597b6f470833de
- https://git.kernel.org/stable/c/eb51f639ef3fd5498b7def290ed8681b6aadd9a7
- https://git.kernel.org/stable/c/f707820c09239d6f67699d9b2ff57863cc7905b0
