# [M] ZimaOS vulnerable to Username Enumeration via API Responses

## Summary
Severity: Medium
Advisory: CVE-2024-49358
Aliases: GHSA-3f6g-8r88-3mx5
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-49358
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In version 1.2.4 and all prior versions, the API endpoint `http://<Server-IP>/v1/users/login` in ZimaOS returns distinct responses based on whether a username exists or the password is incorrect. This behavior can be exploited for username enumeration, allowing attackers to determine whether a user exists in the system or not. Attackers can leverage this information in further attacks, such as credential stuffing or targeted password brute-forcing. As of time of publication, no known patched versions are available.

## References
- https://youtu.be/BClx2u8DMfM
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49358.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-3f6g-8r88-3mx5
- https://nvd.nist.gov/vuln/detail/CVE-2024-49358
