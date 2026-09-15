# [M] Pam: libpam: libpam vulnerable to read hashed password

## Summary
Severity: Medium
Advisory: CVE-2024-10041
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-23
Source: https://osv.dev/vulnerability/CVE-2024-10041
Type: osv

## Details
A vulnerability was found in PAM. The secret information is stored in memory, where the attacker can trigger the victim program to execute by sending characters to its standard input (stdin). As this occurs, the attacker can train the branch predictor to execute an ROP chain speculatively. This flaw could result in leaked passwords, such as those found in /etc/shadow while performing authentications.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:10379
- https://access.redhat.com/errata/RHSA-2024:11250
- https://access.redhat.com/errata/RHSA-2024:9941
- https://access.redhat.com/security/cve/CVE-2024-10041
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10041.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10041
- https://bugzilla.redhat.com/show_bug.cgi?id=2319212
- https://github.com/linux-pam/linux-pam
