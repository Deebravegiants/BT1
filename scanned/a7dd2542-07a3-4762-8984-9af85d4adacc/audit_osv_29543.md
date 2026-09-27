# [H] iio: Fix the sorting functionality in iio_gts_build_avail_time_table

## Summary
Severity: High
Advisory: CVE-2024-43825
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43825
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: Fix the sorting functionality in iio_gts_build_avail_time_table

The sorting in iio_gts_build_avail_time_table is not working as intended.
It could result in an out-of-bounds access when the time is zero.

Here are more details:

1. When the gts->itime_table[i].time_us is zero, e.g., the time
sequence is `3, 0, 1`, the inner for-loop will not terminate and do
out-of-bound writes. This is because once `times[j] > new`, the value
`new` will be added in the current position and the `times[j]` will be
moved to `j+1` position, which makes the if-condition always hold.
Meanwhile, idx will be added one, making the loop keep running without
termination and out-of-bound write.
2. If none of the gts->itime_table[i].time_us is zero, the elements
will just be copied without being sorted as described in the comment
"Sort times from all tables to one and remove duplicates".

For more details, please refer to
https://lore.kernel.org/all/6dd0d822-046c-4dd2-9532-79d7ab96ec05@gmail.com.

## References
- https://git.kernel.org/stable/c/31ff8464ef540785344994986a010031410f9ff3
- https://git.kernel.org/stable/c/5acc3f971a01be48d5ff4252d8f9cdb87998cdfb
- https://git.kernel.org/stable/c/b5046de32fd1532c3f67065197fc1da82f0b5193
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43825.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43825
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
