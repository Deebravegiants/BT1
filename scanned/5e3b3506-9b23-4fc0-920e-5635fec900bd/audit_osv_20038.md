# [M] CVE-2021-29488

## Summary
Severity: Medium
Advisory: CVE-2021-29488
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-05-07
Source: https://osv.dev/vulnerability/CVE-2021-29488
Type: osv

## Details
SABnzbd is an open source binary newsreader. A vulnerability was discovered in SABnzbd that could trick the `filesystem.renamer()` function into writing downloaded files outside the configured Download Folder via malicious PAR2 files. A patch was released as part of SABnzbd 3.2.1RC1. As a workaround, limit downloads to NZBs without PAR2 files, deny write permissions to the SABnzbd process outside areas it must access to perform its job, or update to a fixed version.

## References
- https://github.com/sabnzbd/sabnzbd/security/advisories/GHSA-jwj3-wrvf-v3rp
