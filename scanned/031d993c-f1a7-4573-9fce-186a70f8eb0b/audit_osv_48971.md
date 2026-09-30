# [M] CVE-2018-19208

## Summary
Severity: Medium
Advisory: CVE-2018-19208
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19208
Type: osv

## Details
In libwpd 0.10.2, there is a NULL pointer dereference in the function WP6ContentListener::defineTable in WP6ContentListener.cpp that will lead to a denial of service attack. This is related to WPXTable.h.

## References
- https://access.redhat.com/errata/RHSA-2019:2126
- https://bugzilla.redhat.com/show_bug.cgi?id=1643752
