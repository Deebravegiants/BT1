# [M] Nexus Repository 3 - Static hard-coded encryption passphrase used by default

## Summary
Severity: Medium
Advisory: CVE-2024-5764
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-10-23
Source: https://osv.dev/vulnerability/CVE-2024-5764
Type: osv

## Details
Use of Hard-coded Credentials vulnerability in Sonatype Nexus Repository has been discovered in the code responsible for encrypting any secrets stored in the Nexus Repository configuration database (SMTP or HTTP proxy credentials, user tokens, tokens, among others). The affected versions relied on a static hard-coded encryption passphrase. While it was possible for an administrator to define an alternate encryption passphrase, it could only be done at first boot and not updated.

This issue affects Nexus Repository: from 3.0.0 through 3.72.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5764.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5764
- https://support.sonatype.com/hc/en-us/articles/34496708991507
