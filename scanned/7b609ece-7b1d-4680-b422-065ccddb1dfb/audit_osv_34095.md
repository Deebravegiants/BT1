# [H] LocalSend is Vulnerable to Man-in-the-Middle Attacks, Leading to File Interception

## Summary
Severity: High
Advisory: CVE-2025-54792
Aliases: GHSA-424h-5f6m-x63f
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2025-08-01
Source: https://osv.dev/vulnerability/CVE-2025-54792
Type: osv

## Details
LocalSend is an open-source app to securely share files and messages with nearby devices over local networks without needing an internet connection. In versions 1.16.1 and below, a critical Man-in-the-Middle (MitM) vulnerability in the software's discovery protocol allows an unauthenticated attacker on the same local network to impersonate legitimate devices, silently intercepting, reading, and modifying any file transfer. This can be used to steal sensitive data or inject malware, like ransomware, into files shared between trusted users. The attack is hardly detectable and easy to implement, posing a severe and immediate security risk. This issue was fixed in version 1.17.0.

## References
- https://github.com/localsend/localsend/releases/tag/v1.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54792.json
- https://github.com/localsend/localsend/security/advisories/GHSA-424h-5f6m-x63f
- https://nvd.nist.gov/vuln/detail/CVE-2025-54792
- https://github.com/localsend/localsend/commit/e8635204ec782ded45bc7d698deb60f3c4105687
