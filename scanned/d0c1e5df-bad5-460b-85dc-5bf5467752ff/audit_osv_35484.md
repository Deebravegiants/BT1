# [H] Libtiff: libtiff write-what-where

## Summary
Severity: High
Advisory: CVE-2025-9900
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-9900
Type: osv

## Details
A flaw was found in Libtiff. This vulnerability is a "write-what-where" condition, triggered when the library processes a specially crafted TIFF image file.

By providing an abnormally large image height value in the file's metadata, an attacker can trick the library into writing attacker-controlled color data to an arbitrary memory location. This memory corruption can be exploited to cause a denial of service (application crash) or to achieve arbitrary code execution with the permissions of the user.

## References
- http://www.openwall.com/lists/oss-security/2025/09/26/3
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://libtiff.gitlab.io/libtiff/
- https://lists.debian.org/debian-lts-announce/2025/09/msg00031.html
- https://access.redhat.com/errata/RHSA-2025:17651
- https://access.redhat.com/errata/RHSA-2025:17675
- https://access.redhat.com/errata/RHSA-2025:17710
- https://access.redhat.com/errata/RHSA-2025:17738
- https://access.redhat.com/errata/RHSA-2025:17739
- https://access.redhat.com/errata/RHSA-2025:17740
- https://access.redhat.com/errata/RHSA-2025:19113
- https://access.redhat.com/errata/RHSA-2025:19156
- https://access.redhat.com/errata/RHSA-2025:19276
- https://access.redhat.com/errata/RHSA-2025:19906
- https://access.redhat.com/errata/RHSA-2025:19947
- https://access.redhat.com/errata/RHSA-2025:20956
- https://access.redhat.com/errata/RHSA-2025:20998
- https://access.redhat.com/errata/RHSA-2025:21060
- https://access.redhat.com/errata/RHSA-2025:21061
