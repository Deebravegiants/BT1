# [H] Open OnDemand didn't rotate password for VNC batch_connect

## Summary
Severity: High
Advisory: CVE-2025-58435
Aliases: GHSA-7vh8-mw9f-5r99
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-58435
Type: osv

## Details
Open OnDemand is an open-source HPC portal. Prior to versions 3.1.15 and 4.0.7, noVNC interactive applications did not correctly rotate the password when TurboVNC was higher than version 3.1.2. The likelihood of exploitation is low as a user would need to share their link to an active desktop session and the other user would need to be authenticated to the portal. But obtaining the link would allow that user to perform any actions as the original user and access their data. Open OnDemand 3.1.15 and 4.0.7 have patched this vulnerability and correctly rotate passwords for any version of TurboVNC. As a workaround, downgrade TurboVNC to a version lower than 3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58435.json
- https://github.com/OSC/ondemand/security/advisories/GHSA-7vh8-mw9f-5r99
- https://nvd.nist.gov/vuln/detail/CVE-2025-58435
