# [M] CVE-2021-47050

## Summary
Severity: Medium
Advisory: CVE-2021-47050
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47050
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

memory: renesas-rpc-if: fix possible NULL pointer dereference of resource

The platform_get_resource_byname() can return NULL which would be
immediately dereferenced by resource_size().  Instead dereference it
after validating the resource.

Addresses-Coverity: Dereference null return value

## References
- https://git.kernel.org/stable/c/59e27d7c94aa02da039b000d33c304c179395801
- https://git.kernel.org/stable/c/71bcc1b4a1743534d8abdcb57ff912e6bc390438
- https://git.kernel.org/stable/c/a74cb41af7dbe019e4096171f8bc641c7ce910ad
- https://git.kernel.org/stable/c/e16acc3a37f09e18835dc5d8014942c2ef6ca957
