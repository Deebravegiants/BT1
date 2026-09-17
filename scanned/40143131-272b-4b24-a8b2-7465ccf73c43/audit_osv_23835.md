# [H] zsmalloc: fix races between asynchronous zspage free and page migration

## Summary
Severity: High
Advisory: CVE-2022-49554
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49554
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.14.282, >=4.15.0 <4.19.246, >=4.20.0 <5.4.197, >=5.5.0 <5.10.120, >=5.11.0 <5.15.45, >=5.16.0 <5.17.13, >=5.18.0 <5.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

zsmalloc: fix races between asynchronous zspage free and page migration

The asynchronous zspage free worker tries to lock a zspage's entire page
list without defending against page migration.  Since pages which haven't
yet been locked can concurrently migrate off the zspage page list while
lock_zspage() churns away, lock_zspage() can suffer from a few different
lethal races.

It can lock a page which no longer belongs to the zspage and unsafely
dereference page_private(), it can unsafely dereference a torn pointer to
the next page (since there's a data race), and it can observe a spurious
NULL pointer to the next page and thus not lock all of the zspage's pages
(since a single page migration will reconstruct the entire page list, and
create_page_chain() unconditionally zeroes out each list pointer in the
process).

Fix the races by using migrate_read_lock() in lock_zspage() to synchronize
with page migration.

## References
- https://git.kernel.org/stable/c/2505a981114dcb715f8977b8433f7540854851d8
- https://git.kernel.org/stable/c/3674d8a8dadd03a447dd21069d4dacfc3399b63b
- https://git.kernel.org/stable/c/3ec459c8810e658401be428d3168eacfc380bdd0
- https://git.kernel.org/stable/c/645996efc2ae391246d595832aaa6f9d3cc338c7
- https://git.kernel.org/stable/c/8ba7b7c1dad1f6503c541778f31b33f7f62eb966
- https://git.kernel.org/stable/c/c5402fb5f71f1a725f1e55d9c6799c0c7bec308f
- https://git.kernel.org/stable/c/fae05b2314b147a78fbed1dc4c645d9a66313758
- https://git.kernel.org/stable/c/fc658c083904427abbf8f18280d517ee2668677c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49554.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49554
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
