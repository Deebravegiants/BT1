# [H] wifi: mac80211: use safe list iteration in radar detect work

## Summary
Severity: High
Advisory: CVE-2026-46166
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46166
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: use safe list iteration in radar detect work

The call to ieee80211_dfs_cac_cancel can cause the iterated chanctx to
be freed and removed from the list. Guard against this to avoid a
slab-use-after-free error.

## References
- https://git.kernel.org/stable/c/120149fb3ebcf674832ca3cafd32bedcdb686dde
- https://git.kernel.org/stable/c/7577a4b8a10fab45a6ee2045ea038a5adadbb585
- https://git.kernel.org/stable/c/887ece6c23b49d02a6678e7a8d5ad213d75883ce
- https://git.kernel.org/stable/c/ac8eb3e18f41e2cc8492cc1d358bcb786c850270
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46166.json
- https://access.redhat.com/errata/RHSA-2026:27288
- https://access.redhat.com/errata/RHSA-2026:27708
- https://access.redhat.com/errata/RHSA-2026:27789
- https://access.redhat.com/errata/RHSA-2026:33215
- https://access.redhat.com/security/cve/CVE-2026-46166
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46166.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46166
- https://bugzilla.redhat.com/show_bug.cgi?id=2482645
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
