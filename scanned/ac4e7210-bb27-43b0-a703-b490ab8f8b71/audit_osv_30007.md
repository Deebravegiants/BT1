# [M] ZimaOS Unauthenticated API Discloses Usernames

## Summary
Severity: Medium
Advisory: CVE-2024-48932
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-48932
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In versions below 1.5.0, the API endpoint `http://<Server-ip>/v1/users/name` allows unauthenticated users to access sensitive information, such as usernames, without any authorization. This vulnerability could be exploited by an attacker to enumerate usernames and leverage them for further attacks, such as brute-force or phishing campaigns. As of time of publication, no known patched versions are available.

## References
- https://youtu.be/wJFq8cuyFm4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48932.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-57r9-43pc-gcp2
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-9mrr-px2c-w42c
- https://nvd.nist.gov/vuln/detail/CVE-2024-48932
