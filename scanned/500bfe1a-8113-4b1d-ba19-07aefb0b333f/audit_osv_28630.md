# [H] btrfs: fix race in read_extent_buffer_pages()

## Summary
Severity: High
Advisory: CVE-2024-35798
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35798
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix race in read_extent_buffer_pages()

There are reports from tree-checker that detects corrupted nodes,
without any obvious pattern so possibly an overwrite in memory.
After some debugging it turns out there's a race when reading an extent
buffer the uptodate status can be missed.

To prevent concurrent reads for the same extent buffer,
read_extent_buffer_pages() performs these checks:

    /* (1) */
    if (test_bit(EXTENT_BUFFER_UPTODATE, &eb->bflags))
        return 0;

    /* (2) */
    if (test_and_set_bit(EXTENT_BUFFER_READING, &eb->bflags))
        goto done;

At this point, it seems safe to start the actual read operation. Once
that completes, end_bbio_meta_read() does

    /* (3) */
    set_extent_buffer_uptodate(eb);

    /* (4) */
    clear_bit(EXTENT_BUFFER_READING, &eb->bflags);

Normally, this is enough to ensure only one read happens, and all other
callers wait for it to finish before returning.  Unfortunately, there is
a racey interleaving:

    Thread A | Thread B | Thread C
    ---------+----------+---------
       (1)   |          |
             |    (1)   |
       (2)   |          |
       (3)   |          |
       (4)   |          |
             |    (2)   |
             |          |    (1)

When this happens, thread B kicks of an unnecessary read. Worse, thread
C will see UPTODATE set and return immediately, while the read from
thread B is still in progress.  This race could result in tree-checker
errors like this as the extent buffer is concurrently modified:

    BTRFS critical (device dm-0): corrupted node, root=256
    block=8550954455682405139 owner mismatch, have 11858205567642294356
    expect [256, 18446744073709551360]

Fix it by testing UPTODATE again after setting the READING bit, and if
it's been set, skip the unnecessary read.

[ minor update of changelog ]

## References
- https://git.kernel.org/stable/c/0427c8ef8bbb7f304de42ef51d69c960e165e052
- https://git.kernel.org/stable/c/2885d54af2c2e1d910e20d5c8045bae40e02fbc1
- https://git.kernel.org/stable/c/3a25878a3378adce5d846300c9570f15aa7f7a80
- https://git.kernel.org/stable/c/ef1e68236b9153c27cb7cf29ead0c532870d4215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35798.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35798
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
