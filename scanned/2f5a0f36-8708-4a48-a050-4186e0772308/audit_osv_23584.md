# [H] btrfs: do not double complete bio on errors during compressed reads

## Summary
Severity: High
Advisory: CVE-2022-49167
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49167
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: do not double complete bio on errors during compressed reads

I hit some weird panics while fixing up the error handling from
btrfs_lookup_bio_sums().  Turns out the compression path will complete
the bio we use if we set up any of the compression bios and then return
an error, and then btrfs_submit_data_bio() will also call bio_endio() on
the bio.

Fix this by making btrfs_submit_compressed_read() responsible for
calling bio_endio() on the bio if there are any errors.  Currently it
was only doing it if we created the compression bios, otherwise it was
depending on btrfs_submit_data_bio() to do the right thing.  This
creates the above problem, so fix up btrfs_submit_compressed_read() to
always call bio_endio() in case of an error, and then simply return from
btrfs_submit_data_bio() if we had to call
btrfs_submit_compressed_read().

## References
- https://git.kernel.org/stable/c/4a4ceb2b990771c374d85d496a1a45255dde48e3
- https://git.kernel.org/stable/c/987b5df1d10355d377315a26e7fb6c72ded83c9f
- https://git.kernel.org/stable/c/f9f15de85d74e7eef021af059ca53a15f041cdd8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49167.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49167
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
