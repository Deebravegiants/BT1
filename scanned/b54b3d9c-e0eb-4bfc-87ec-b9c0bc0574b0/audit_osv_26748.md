# [H] accel/qaic: Clean up integer overflow checking in map_user_pages()

## Summary
Severity: High
Advisory: CVE-2023-53778
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53778
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/qaic: Clean up integer overflow checking in map_user_pages()

The encode_dma() function has some validation on in_trans->size but it
would be more clear to move those checks to find_and_map_user_pages().

The encode_dma() had two checks:

	if (in_trans->addr + in_trans->size < in_trans->addr || !in_trans->size)
		return -EINVAL;

The in_trans->addr variable is the starting address.  The in_trans->size
variable is the total size of the transfer.  The transfer can occur in
parts and the resources->xferred_dma_size tracks how many bytes we have
already transferred.

This patch introduces a new variable "remaining" which represents the
amount we want to transfer (in_trans->size) minus the amount we have
already transferred (resources->xferred_dma_size).

I have modified the check for if in_trans->size is zero to instead check
if in_trans->size is less than resources->xferred_dma_size.  If we have
already transferred more bytes than in_trans->size then there are negative
bytes remaining which doesn't make sense.  If there are zero bytes
remaining to be copied, just return success.

The check in encode_dma() checked that "addr + size" could not overflow
and barring a driver bug that should work, but it's easier to check if
we do this in parts.  First check that "in_trans->addr +
resources->xferred_dma_size" is safe.  Then check that "xfer_start_addr +
remaining" is safe.

My final concern was that we are dealing with u64 values but on 32bit
systems the kmalloc() function will truncate the sizes to 32 bits.  So
I calculated "total = in_trans->size + offset_in_page(xfer_start_addr);"
and returned -EINVAL if it were >= SIZE_MAX.  This will not affect 64bit
systems.

## References
- https://git.kernel.org/stable/c/96d3c1cadedb6ae2e8965e19cd12caa244afbd9c
- https://git.kernel.org/stable/c/d410a96e5cb8c1ec7049c83f2edcd8bbfaf5d9b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53778.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53778
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
