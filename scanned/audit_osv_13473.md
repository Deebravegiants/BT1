# [M] CVE-2018-1999020

## Summary
Severity: Medium
Advisory: CVE-2018-1999020
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999020
Type: osv

## Details
Open Networking Foundation (ONF) ONOS version 1.13.2 and earlier version contains a Directory Traversal vulnerability in core/common/src/main/java/org/onosproject/common/app/ApplicationArchive.java line 35 that can result in arbitrary file deletion (overwrite). This attack appear to be exploitable via a specially crafted zip file should be uploaded.

## References
- https://gerrit.onosproject.org/#/c/19043/
- http://gms.cl0udz.com/ONOS_app_overwrite.pdf
