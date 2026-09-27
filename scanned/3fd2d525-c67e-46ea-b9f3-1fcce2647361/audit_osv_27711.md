# [C] CVE-2024-25140

## Summary
Severity: Critical
Advisory: CVE-2024-25140
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-25140
Type: osv

## Details
A default installation of RustDesk 1.2.3 on Windows places a WDKTestCert certificate under Trusted Root Certification Authorities with Enhanced Key Usage of Code Signing (1.3.6.1.5.5.7.3.3), valid from 2023 until 2033. This is potentially unwanted, e.g., because there is no public documentation of security measures for the private key, and arbitrary software could be signed if the private key were to be compromised. NOTE: the vendor's position is "we do not have EV cert, so we use test cert as a workaround." Insertion into Trusted Root Certification Authorities was the originally intended behavior, and the UI ensured that the certificate installation step (checked by default) was visible to the user before proceeding with the product installation.

## References
- https://github.com/rustdesk/rustdesk/discussions/6444
- https://news.ycombinator.com/item?id=39256493
- https://serverfault.com/questions/837994
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25140.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25140
