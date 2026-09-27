# [H] tracing: Prevent out-of-bounds read in glob matching

## Summary
Severity: High
Advisory: CVE-2026-64299
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64299
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Prevent out-of-bounds read in glob matching

String event fields are not necessarily NUL-terminated, so the filter
predicate functions (filter_pred_string(), filter_pred_strloc() and
filter_pred_strrelloc()) pass the field length to the regex match
callbacks, and the length-aware matchers honour it.

regex_match_glob() was the exception: it ignored the length and called
glob_match(), which scans the string until it hits a NUL byte. Some
string fields are not NUL-terminated. One example is the dynamic char
array of the xfs_* namespace tracepoints, which is copied without a
trailing NUL. For such a field, glob matching reads past the end of
the event field, causing a KASAN slab-out-of-bounds read in
glob_match(), reached via regex_match_glob() and filter_match_preds()
from the xfs_lookup tracepoint.

Add a length-bounded glob_match_len() and use it from regex_match_glob()
so glob matching always stops at the field boundary. The matching loop
is factored into a shared helper so glob_match() keeps its behaviour.

## References
- https://git.kernel.org/stable/c/0a6070839b1ef276d5b05bedfb787743e140fb17
- https://git.kernel.org/stable/c/265f3a690f6c7d69ef7d2ca50b04b4853a211df3
- https://git.kernel.org/stable/c/2dad64a97e1df47f5d9ccb17fa319aa348617226
- https://git.kernel.org/stable/c/35ae19764eabfe9c29029d3b5713c86e6855acdf
- https://git.kernel.org/stable/c/56d4c9ab84714eebb285a2fee68aaedf81e3ef15
- https://git.kernel.org/stable/c/e5d5f3bd053a5f14787526c9f0f55ef900d43ac6
- https://git.kernel.org/stable/c/ebb55902856973906c8bb339a3a34824ed4a5086
- https://git.kernel.org/stable/c/ee5b8888d3248618251fb69a2fad92afcb81557e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64299.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64299
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
