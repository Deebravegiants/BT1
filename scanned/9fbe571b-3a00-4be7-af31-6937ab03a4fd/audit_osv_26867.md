# [H] blk-mq: fix tags leak when shrink nr_hw_queues

## Summary
Severity: High
Advisory: CVE-2023-54227
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54227
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-mq: fix tags leak when shrink nr_hw_queues

Although we don't need to realloc set->tags[] when shrink nr_hw_queues,
we need to free them. Or these tags will be leaked.

How to reproduce:
1. mount -t configfs configfs /mnt
2. modprobe null_blk nr_devices=0 submit_queues=8
3. mkdir /mnt/nullb/nullb0
4. echo 1 > /mnt/nullb/nullb0/power
5. echo 4 > /mnt/nullb/nullb0/submit_queues
6. rmdir /mnt/nullb/nullb0

In step 4, will alloc 9 tags (8 submit queues and 1 poll queue), then
in step 5, new_nr_hw_queues = 5 (4 submit queues and 1 poll queue).
At last in step 6, only these 5 tags are freed, the other 4 tags leaked.

## References
- https://git.kernel.org/stable/c/c0ef7493e68b8896806a2f598fcffbaa97333405
- https://git.kernel.org/stable/c/e1dd7bc93029024af5688253b0c05181d6e01f8e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54227.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54227
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
