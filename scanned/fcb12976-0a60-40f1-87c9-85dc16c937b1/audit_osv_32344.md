# [M] Collabora Online Vulnerable to Arbitrary File Write

## Summary
Severity: Medium
Advisory: CVE-2025-27791
Aliases: GHSA-9j32-gg3j-8w25
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-27791
Type: osv

## Details
Collabora Online is a collaborative online office suite based on LibreOffice technology. In versions prior to 24.04.12.4, 23.05.19, and 22.05.25, there is a path traversal flaw in handling the CheckFileInfo BaseFileName field returned from WOPI servers. This allows for a file to be written anywhere the uid running Collabora Online can write, if such a response was supplied by a malicious WOPI server. By combining this flaw with a Time of Check, Time of Use DNS lookup issue with a WOPI server address under attacker control, it is possible to present such a response to be processed by a Collabora Online instance. This issue has been patched in versions 24.04.13.1, 23.05.19, and 22.05.25.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27791.json
- https://github.com/CollaboraOnline/online/security/advisories/GHSA-9j32-gg3j-8w25
- https://nvd.nist.gov/vuln/detail/CVE-2025-27791
