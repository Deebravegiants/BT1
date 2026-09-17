# [M] trace_events_hist: add check for return value of 'create_hist_field'

## Summary
Severity: Medium
Advisory: CVE-2023-53005
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53005
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.272, >=4.20.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

trace_events_hist: add check for return value of 'create_hist_field'

Function 'create_hist_field' is called recursively at
trace_events_hist.c:1954 and can return NULL-value that's why we have
to check it to avoid null pointer dereference.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/31b2414abeaa6de0490e85164badc6dcb1bb8ec9
- https://git.kernel.org/stable/c/592ba7116fa620425725ff0972691f352ba3caf6
- https://git.kernel.org/stable/c/886aa449235f478e262bbd5dcdee6ed6bc202949
- https://git.kernel.org/stable/c/8b152e9150d07a885f95e1fd401fc81af202d9a4
- https://git.kernel.org/stable/c/b4e7e81b4fdfcf457daee6b7a61769f62198d840
- https://git.kernel.org/stable/c/d2d1ada58e7cc100b8d7d6b082d19321ba4a700a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53005.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53005
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
