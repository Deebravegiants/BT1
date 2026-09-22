# [H] md/raid10: fix writes_pending and barrier reference leaks on discard failures

## Summary
Severity: High
Advisory: CVE-2026-72438
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72438
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid10: fix writes_pending and barrier reference leaks on discard failures

raid10_make_request() acquires a writes_pending reference with
md_write_start() before calling raid10_handle_discard(). Several failure
paths in raid10_handle_discard() complete the bio and return without
releasing the corresponding reference, causing md_write_end() to be
skipped.

Call md_write_end() before returning from these failure paths to keep
writes_pending accounting balanced.

Additionally, discard split allocation failures can occur after
wait_barrier() succeeds. Those paths return without calling
allow_barrier(), leaking the associated barrier reference.

Release the barrier before returning from those paths.

## References
- https://git.kernel.org/stable/c/393d687131d8aa8c7e4de2cb494438e145d20fc2
- https://git.kernel.org/stable/c/d1324b41dabd26787559efaeb430643c627c1eb0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72438.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72438
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
