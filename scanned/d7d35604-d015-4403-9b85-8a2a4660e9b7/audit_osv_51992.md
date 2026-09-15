# [M] CVE-2021-46935

## Summary
Severity: Medium
Advisory: CVE-2021-46935
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46935
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix async_free_space accounting for empty parcels

In 4.13, commit 74310e06be4d ("android: binder: Move buffer out of area shared with user space")
fixed a kernel structure visibility issue. As part of that patch,
sizeof(void *) was used as the buffer size for 0-length data payloads so
the driver could detect abusive clients sending 0-length asynchronous
transactions to a server by enforcing limits on async_free_size.

Unfortunately, on the "free" side, the accounting of async_free_space
did not add the sizeof(void *) back. The result was that up to 8-bytes of
async_free_space were leaked on every async transaction of 8-bytes or
less.  These small transactions are uncommon, so this accounting issue
has gone undetected for several years.

The fix is to use "buffer_size" (the allocated buffer size) instead of
"size" (the logical buffer size) when updating the async_free_space
during the free operation. These are the same except for this
corner case of asynchronous transactions with payloads < 8 bytes.

## References
- https://git.kernel.org/stable/c/17691bada6b2f1d5f1c0f6d28cd9d0727023b0ff
- https://git.kernel.org/stable/c/1cb8444f3114f0bb2f6e3bcadcf09aa4a28425d4
- https://git.kernel.org/stable/c/2d2df539d05205fd83c404d5f2dff48d36f9b495
- https://git.kernel.org/stable/c/7c7064402609aeb6fb11be1b4ec10673ff17b593
- https://git.kernel.org/stable/c/cfd0d84ba28c18b531648c9d4a35ecca89ad9901
- https://git.kernel.org/stable/c/103b16a8c51f96d5fe063022869ea906c256e5da
