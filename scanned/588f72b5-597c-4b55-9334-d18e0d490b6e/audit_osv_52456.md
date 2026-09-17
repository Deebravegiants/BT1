# [M] CVE-2021-47467

## Summary
Severity: Medium
Advisory: CVE-2021-47467
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47467
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

kunit: fix reference count leak in kfree_at_end

The reference counting issue happens in the normal path of
kfree_at_end(). When kunit_alloc_and_get_resource() is invoked, the
function forgets to handle the returned resource object, whose refcount
increased inside, causing a refcount leak.

Fix this issue by calling kunit_alloc_resource() instead of
kunit_alloc_and_get_resource().

Fixed the following when applying:
Shuah Khan <skhan@linuxfoundation.org>

CHECK: Alignment should match open parenthesis
+	kunit_alloc_resource(test, NULL, kfree_res_free, GFP_KERNEL,
 				     (void *)to_free);

## References
- https://git.kernel.org/stable/c/bbdd158b40b66a9403391a517f24ef6613573446
- https://git.kernel.org/stable/c/f62314b1ced25c58b86e044fc951cd6a1ea234cf
