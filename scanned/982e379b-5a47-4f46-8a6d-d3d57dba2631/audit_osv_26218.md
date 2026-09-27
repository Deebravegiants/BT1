# [H] wifi: mac80211: fix potential key use-after-free

## Summary
Severity: High
Advisory: CVE-2023-52530
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52530
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.4.285, >=5.5.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.57, >=6.2.0 <6.5.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: fix potential key use-after-free

When ieee80211_key_link() is called by ieee80211_gtk_rekey_add()
but returns 0 due to KRACK protection (identical key reinstall),
ieee80211_gtk_rekey_add() will still return a pointer into the
key, in a potential use-after-free. This normally doesn't happen
since it's only called by iwlwifi in case of WoWLAN rekey offload
which has its own KRACK protection, but still better to fix, do
that by returning an error code and converting that to success on
the cfg80211 boundary only, leaving the error for bad callers of
ieee80211_gtk_rekey_add().

## References
- https://git.kernel.org/stable/c/2408f491ff998d674707725eadc47d8930aced09
- https://git.kernel.org/stable/c/2f4e16e39e4f5e78248dd9e51276a83203950b36
- https://git.kernel.org/stable/c/31db78a4923ef5e2008f2eed321811ca79e7f71b
- https://git.kernel.org/stable/c/65c72a7201704574dace708cbc96a8f367b1491d
- https://git.kernel.org/stable/c/e8a834eb09bb95c2bf9c76f1a28ecef7d8c439d0
- https://git.kernel.org/stable/c/e8e599a635066c50ac214c3e10858f1d37e03022
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52530.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52530
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
