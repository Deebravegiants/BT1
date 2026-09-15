# [H] Local Privilege Escalation in Rufus 4.6 and previous versions

## Summary
Severity: High
Advisory: CVE-2025-26624
Aliases: GHSA-p8p5-r296-g2jv
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26624
Type: osv

## Details
Rufus is a utility that helps format and create bootable USB flash drives. A DLL hijacking vulnerability in Rufus 4.6.2208 and earlier versions allows an attacker loading and executing a malicious DLL with escalated privileges (since the executable has been granted higher privileges during the time of launch) due to the ability to inject a malicious `cfgmgr32.dll` in the same directory as the executable and have it side load automatically. This is fixed in commit `74dfa49`, which will be part of version 4.7. Users are advised to upgrade as soon as version 4.7 becomes available. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26624.json
- https://github.com/pbatard/rufus/security/advisories/GHSA-p8p5-r296-g2jv
- https://nvd.nist.gov/vuln/detail/CVE-2025-26624
- https://github.com/pbatard/rufus/commit/74dfa49707fd626b58d776d3400295740a29e23e
