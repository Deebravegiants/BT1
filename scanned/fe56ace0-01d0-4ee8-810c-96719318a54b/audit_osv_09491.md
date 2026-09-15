# [M] CVE-2017-0883

## Summary
Severity: Medium
Advisory: CVE-2017-0883
CVSS: 6.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-0883
Type: osv

## Details
Nextcloud Server before 9.0.55 and 10.0.2 suffers from a permission increase on re-sharing via OCS API issue. A permission related issue within the OCS sharing API allowed an authenticated adversary to reshare shared files with an increasing permission set. This may allow an attacker to edit files in a share despite having only a 'read' permission set. Note that this only affects folders and files that the adversary has at least read-only permissions for.

## References
- https://hackerone.com/reports/169680
- https://nextcloud.com/security/advisory/?id=nc-sa-2017-001
