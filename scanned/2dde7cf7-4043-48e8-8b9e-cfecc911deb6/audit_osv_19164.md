# [M] CVE-2020-8297

## Summary
Severity: Medium
Advisory: CVE-2020-8297
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2020-8297
Type: osv

## Details
Nextcloud Deck before 1.0.2 suffers from an insecure direct object reference (IDOR) vulnerability that permits users with a duplicate user identifier to access deck data of a previous deleted user.

## References
- https://nextcloud.com/security/advisory/?id=NC-SA-2021-007
- https://github.com/nextcloud/deck/pull/1976
- https://hackerone.com/reports/882258
