# [C] CVE-2020-22617

## Summary
Severity: Critical
Advisory: CVE-2020-22617
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-08
Source: https://osv.dev/vulnerability/CVE-2020-22617
Type: osv

## Details
Ardour v5.12 contains a use-after-free vulnerability in the component ardour/libs/pbd/xml++.cc when using xmlFreeDoc and xmlXPathFreeContext.

## References
- https://tracker.ardour.org/view.php?id=7926
- https://github.com/Ardour/ardour/commit/96daa4036a
