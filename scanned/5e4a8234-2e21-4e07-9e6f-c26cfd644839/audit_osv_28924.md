# [C] Shell command injection in Phoniebox

## Summary
Severity: Critical
Advisory: CVE-2024-3799
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-07-10
Source: https://osv.dev/vulnerability/CVE-2024-3799
Type: osv

## Details
Insecure handling of POST header parameter body included in requests being sent to an instance of the open-source project Phoniebox allows an attacker to create a website, which – when visited by a user – will send malicious requests to multiple hosts on the local network. If such a request reaches the server, it will cause a shell command execution.


This issue affects Phoniebox in all releases through 2.7. Newer 2.x releases were not tested, but they might also be vulnerable. 
Phoniebox in version 3.0 and higher are not affected.

## References
- https://cert.pl/en/posts/2024/07/CVE-2024-3798
- https://cert.pl/posts/2024/07/CVE-2024-3798
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3799.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3799
- https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/2342
- https://github.com/MiczFlor/RPi-Jukebox-RFID
