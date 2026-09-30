# [M] CVE-2021-32652

## Summary
Severity: Medium
Advisory: CVE-2021-32652
Aliases: GHSA-mxx2-6rg9-v2vc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-32652
Type: osv

## Details
Nextcloud Mail is a mail app for the Nextcloud platform. A missing permission check in Nextcloud Mail before 1.4.3 and 1.8.2 allows another authenticated users to access mail metadata of other users. Versions 1.4.3 and 1.8.2 contain patches for this vulnerability; no workarounds other than the patches are known to exist.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-mxx2-6rg9-v2vc
- https://hackerone.com/reports/1094063
