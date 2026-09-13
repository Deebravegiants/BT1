# [H] CVE-2021-47138

## Summary
Severity: High
Advisory: CVE-2021-47138
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47138
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxgb4: avoid accessing registers when clearing filters

Hardware register having the server TID base can contain
invalid values when adapter is in bad state (for example,
due to AER fatal error). Reading these invalid values in the
register can lead to out-of-bound memory access. So, fix
by using the saved server TID base when clearing filters.

## References
- https://git.kernel.org/stable/c/285207a558ab456aa7d8aa877ecc7e91fcc51710
- https://git.kernel.org/stable/c/88c380df84fbd03f9b137c2b9d0a44b9f2f553b0
- https://git.kernel.org/stable/c/02f03883fdb10ad7e66717c70ea163a8d27ae6e7
- https://git.kernel.org/stable/c/0bf49b3c8d8b3a43ce09f1b2db70e5484d31fcdf
