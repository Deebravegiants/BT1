# [M] CVE-2023-1183

## Summary
Severity: Medium
Advisory: CVE-2023-1183
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-07-10
Source: https://osv.dev/vulnerability/CVE-2023-1183
Type: osv

## Details
A flaw was found in the Libreoffice package. An attacker can craft an odb containing a "database/script" file with a SCRIPT command where the contents of the file could be written to a new file whose location was determined by the attacker.

## References
- http://www.openwall.com/lists/oss-security/2023/12/28/4
- http://www.openwall.com/lists/oss-security/2024/01/03/4
- https://access.redhat.com/security/cve/CVE-2023-1183
- https://bugzilla.redhat.com/show_bug.cgi?id=2208506
- https://www.libreoffice.org/about-us/security/advisories/cve-2023-1183/
