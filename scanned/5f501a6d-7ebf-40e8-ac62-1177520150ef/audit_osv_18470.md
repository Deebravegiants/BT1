# [H] CVE-2020-27823

## Summary
Severity: High
Advisory: CVE-2020-27823
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2020-27823
Type: osv

## Details
A flaw was found in OpenJPEG’s encoder. This flaw allows an attacker to pass specially crafted x,y offset input to OpenJPEG to use during encoding. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OQR4EWRFFZQDMFPZKFZ6I3USLMW6TKTP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJUPGIZE6A4O52EBOF75MCXJOL6MUCRV/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00011.html
- https://www.debian.org/security/2021/dsa-4882
- https://bugzilla.redhat.com/show_bug.cgi?id=1905762
