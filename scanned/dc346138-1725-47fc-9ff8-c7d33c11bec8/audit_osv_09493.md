# [M] CVE-2017-0885

## Summary
Severity: Medium
Advisory: CVE-2017-0885
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-0885
Type: osv

## Details
Nextcloud Server before 9.0.55 and 10.0.2 suffers from a error message disclosing existence of file in write-only share. Due to an error in the application logic an adversary with access to a write-only share may enumerate the names of existing files and subfolders by comparing the exception messages.

## References
- https://hackerone.com/reports/174524
- https://nextcloud.com/security/advisory/?id=nc-sa-2017-003
