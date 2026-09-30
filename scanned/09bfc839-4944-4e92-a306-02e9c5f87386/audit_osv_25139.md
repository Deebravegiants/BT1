# [M] CVE-2023-31437

## Summary
Severity: Medium
Advisory: CVE-2023-31437
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-06-13
Source: https://osv.dev/vulnerability/CVE-2023-31437
Type: osv

## Details
An issue was discovered in systemd 253. An attacker can modify a sealed log file such that, in some views, not all existing and sealed log messages are displayed. NOTE: the vendor reportedly sent "a reply denying that any of the finding was a security vulnerability."

## References
- https://github.com/kastel-security/Journald/blob/main/journald-publication.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31437.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31437
- https://github.com/kastel-security/Journald
- https://github.com/systemd/systemd/releases
