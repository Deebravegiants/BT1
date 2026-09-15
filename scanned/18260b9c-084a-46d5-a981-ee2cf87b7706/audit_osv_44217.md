# [C] netfilter: nf_conntrack_irc: fix parse_dcc() off-by-one OOB read

## Summary
Severity: Critical
Advisory: CVE-2026-80603
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80603
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_irc: fix parse_dcc() off-by-one OOB read

parse_dcc() treats data_end as an inclusive end pointer, but its only
caller passes data_limit = ib_ptr + datalen, which points one past the
last valid byte.

The newline search loop iterates while tmp <= data_end, so when no
newline is present, *tmp is read at tmp == data_end, one byte beyond
the region filled by skb_header_pointer().

irc_buffer is kmalloc'd as MAX_SEARCH_SIZE + 1 bytes and datalen is
capped at MAX_SEARCH_SIZE, so the stray read does not fault.  The byte
is uninitialized or stale; if it contains an ASCII digit, simple_strtoul
will consume it and produce a wrong DCC IP or port in the conntrack
expectation.  The extra allocation byte is also a fragile guard: if the
cap or allocation size changes, this becomes a real out-of-bounds read.

Change the loop and its post-loop check to use strict less-than,
consistent with the caller's exclusive-end convention.  Update the
function comment accordingly.

## References
- https://git.kernel.org/stable/c/2393f0bd7a467ad475598f3a5b9de27ca36e3037
- https://git.kernel.org/stable/c/2b70f61f569bb29acb380e6f616a1bbdee15668f
- https://git.kernel.org/stable/c/437e0a3854b3a44ec15afa9ab88ec215adf3a2fd
- https://git.kernel.org/stable/c/910c33e4a8c046c3cc1fa5a465a4d41a1bb398f1
- https://git.kernel.org/stable/c/abb8c32b88ea3f46beb68c34fe9a3ac8ed664e7e
- https://git.kernel.org/stable/c/aff589556ed772cb1c0c2d7b4d91ec45c0c39416
- https://git.kernel.org/stable/c/eeef3b81f449560653662df2dde6f6fe247c5365
- https://git.kernel.org/stable/c/ef6400ca25a13fd6dedbe8ef4a1d0979bbbfe88a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80603.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80603
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
