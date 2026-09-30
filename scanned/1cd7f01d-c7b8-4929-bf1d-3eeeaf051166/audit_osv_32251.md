# [H] Xorg: xwayland: heap overflow in xkbwritekeysyms()

## Summary
Severity: High
Advisory: CVE-2025-26596
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-25
Source: https://osv.dev/vulnerability/CVE-2025-26596
Type: osv

## Details
A heap overflow flaw was found in X.Org and Xwayland. The computation of the length in XkbSizeKeySyms() differs from what is written in XkbWriteKeySyms(), which may lead to a heap-based buffer overflow.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/02/msg00036.html
- https://access.redhat.com/errata/RHSA-2025:2500
- https://access.redhat.com/errata/RHSA-2025:2502
- https://access.redhat.com/errata/RHSA-2025:2861
- https://access.redhat.com/errata/RHSA-2025:2862
- https://access.redhat.com/errata/RHSA-2025:2865
- https://access.redhat.com/errata/RHSA-2025:2866
- https://access.redhat.com/errata/RHSA-2025:2873
- https://access.redhat.com/errata/RHSA-2025:2874
- https://access.redhat.com/errata/RHSA-2025:2875
- https://access.redhat.com/errata/RHSA-2025:2879
- https://access.redhat.com/errata/RHSA-2025:2880
- https://access.redhat.com/errata/RHSA-2025:3976
- https://access.redhat.com/errata/RHSA-2025:7163
- https://access.redhat.com/errata/RHSA-2025:7165
- https://access.redhat.com/errata/RHSA-2025:7458
- https://access.redhat.com/security/cve/CVE-2025-26596
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26596.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26596
