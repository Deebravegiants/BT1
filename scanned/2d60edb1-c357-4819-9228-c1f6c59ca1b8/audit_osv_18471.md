# [M] CVE-2020-27824

## Summary
Severity: Medium
Advisory: CVE-2020-27824
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2020-27824
Type: osv

## Details
A flaw was found in OpenJPEG’s encoder in the opj_dwt_calc_explicit_stepsizes() function. This flaw allows an attacker who can supply crafted input to decomposition levels to cause a buffer overflow. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OQR4EWRFFZQDMFPZKFZ6I3USLMW6TKTP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJUPGIZE6A4O52EBOF75MCXJOL6MUCRV/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00011.html
- https://www.debian.org/security/2021/dsa-4882
- https://bugzilla.redhat.com/show_bug.cgi?id=1905723
- https://www.oracle.com/security-alerts/cpuoct2021.html
