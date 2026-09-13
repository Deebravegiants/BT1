# [H] CVE-2018-7685

## Summary
Severity: High
Advisory: CVE-2018-7685
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-31
Source: https://osv.dev/vulnerability/CVE-2018-7685
Type: osv

## Details
The decoupled download and installation steps in libzypp before 17.5.0 could lead to a corrupted RPM being left in the cache, where a later call would not display the corrupted RPM warning and allow installation, a problem caused by malicious warnings only displayed during download.

## References
- http://lists.suse.com/pipermail/sle-security-updates/2018-August/004510.html
- https://www.suse.com/de-de/security/cve/CVE-2018-7685/
- https://bugzilla.suse.com/show_bug.cgi?id=1091624
