# [M] CVE-2021-47365

## Summary
Severity: Medium
Advisory: CVE-2021-47365
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47365
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix page leak

There's a loop in afs_extend_writeback() that adds extra pages to a write
we want to make to improve the efficiency of the writeback by making it
larger.  This loop stops, however, if we hit a page we can't write back
from immediately, but it doesn't get rid of the page ref we speculatively
acquired.

This was caused by the removal of the cleanup loop when the code switched
from using find_get_pages_contig() to xarray scanning as the latter only
gets a single page at a time, not a batch.

Fix this by putting the page on a ref on an early break from the loop.
Unfortunately, we can't just add that page to the pagevec we're employing
as we'll go through that and add those pages to the RPC call.

This was found by the generic/074 test.  It leaks ~4GiB of RAM each time it
is run - which can be observed with "top".

## References
- https://git.kernel.org/stable/c/581b2027af0018944ba301d68e7af45c6d1128b5
- https://git.kernel.org/stable/c/d130b5fdd42254d92948d06347940276140c927e
