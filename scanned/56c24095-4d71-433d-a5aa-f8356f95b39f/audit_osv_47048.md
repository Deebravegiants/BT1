# [M] CVE-2015-8791

## Summary
Severity: Medium
Advisory: CVE-2015-8791
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2016-01-29
Source: https://osv.dev/vulnerability/CVE-2015-8791
Type: osv

## Details
The EbmlElement::ReadCodedSizeValue function in libEBML before 1.3.3 allows context-dependent attackers to obtain sensitive information from process heap memory via a crafted length value in an EBML id, which triggers an invalid memory access.

## References
- http://lists.matroska.org/pipermail/matroska-users/2015-October/006985.html
- http://www.debian.org/security/2016/dsa-3538
- https://github.com/Matroska-Org/libebml/blob/release-1.3.3/ChangeLog
- https://github.com/Matroska-Org/libebml/commit/24e5cd7c666b1ddd85619d60486db0a5481c1b90
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00035.html
