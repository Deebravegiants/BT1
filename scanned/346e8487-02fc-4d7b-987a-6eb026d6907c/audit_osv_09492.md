# [M] CVE-2017-0884

## Summary
Severity: Medium
Advisory: CVE-2017-0884
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-0884
Type: osv

## Details
Nextcloud Server before 9.0.55 and 10.0.2 suffers from a creation of folders in read-only folders despite lacking permissions issue. Due to a logical error in the file caching layer an authenticated adversary is able to create empty folders inside a shared folder. Note that this only affects folders and files that the adversary has at least read-only permissions for.

## References
- https://hackerone.com/reports/169680
- https://nextcloud.com/security/advisory/?id=nc-sa-2017-002
