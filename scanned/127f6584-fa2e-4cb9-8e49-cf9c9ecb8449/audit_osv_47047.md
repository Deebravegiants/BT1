# [M] CVE-2015-8790

## Summary
Severity: Medium
Advisory: CVE-2015-8790
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2016-01-29
Source: https://osv.dev/vulnerability/CVE-2015-8790
Type: osv

## Details
The EbmlUnicodeString::UpdateFromUTF8 function in libEBML before 1.3.3 allows context-dependent attackers to obtain sensitive information from process heap memory via a crafted UTF-8 string, which triggers an invalid memory access.

## References
- http://lists.matroska.org/pipermail/matroska-users/2015-October/006985.html
- http://www.debian.org/security/2016/dsa-3538
- https://github.com/Matroska-Org/libebml/blob/release-1.3.3/ChangeLog
- https://github.com/Matroska-Org/libebml/commit/ababb64e0c792ad2a314245233db0833ba12036b
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00035.html
- http://www.securityfocus.com/bid/85307
- http://www.securityfocus.com/bid/95124
- http://www.talosintelligence.com/reports/TALOS-2016-0036/
