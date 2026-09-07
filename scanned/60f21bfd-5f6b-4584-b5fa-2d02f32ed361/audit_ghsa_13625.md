# [C] JWT token compromise can allow malicious actions including Remote Code Execution (RCE) 

## Summary
Severity: Critical
Advisory: GHSA-622h-h2p8-743x
CVE: CVE-2023-32188
CWE: CWE-1270
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2023-10-06
Source: https://github.com/advisories/GHSA-622h-h2p8-743x
Type: github-advisory

## Affected
- Go: `github.com/neuvector/neuvector` — affected >=0 <0.0.0-20231003121714-be746957ee7c

## Details
### Impact 

A user can reverse engineer the JWT token (JSON Web Token) used in authentication for Manager and API access, forging a valid NeuVector Token to perform malicious activity in NeuVector. This can lead to an RCE. 

### Patches 

Upgrade to NeuVector [version 5.2.2](https://open-docs.neuvector.com/releasenotes/5x) or later and latest Helm chart (2.6.3+). 
+ In 5.2.2 the certificate for JWT-signing is created automatically by controller with validity of 90days and rotated automatically.
+ Use Helm-based deployment/upgrade to 5.2.2 to generate a unique certificate for Manager, REST API, ahd registry adapter. Helm based installation/upgrade is required in order to automatically generate certificates upon initial installation and each subsequent upgrade. 
+ See [release notes](https://open-docs.neuvector.com/releasenotes/5x) for manual/yaml based deployment advice.
+ 5.2.2 also implements additional protections against possible RCE for the feature of custom compliance scripts. 

### Workarounds 

Users can replace the Manager & Controller certificate manually by following the instructions in documented [here](https://open-docs.neuvector.com/configuration/console/replacecert). However, upgrading to 5.2.2 and replacing Manager/REST API certificate is recommended to provide additional security enhancements to prevent possible attempted exploit and resulting RCE. See [release notes](https://open-docs.neuvector.com/releasenotes/5x) for additional details.

### Credits 

Thank you to [Dejan Zelic](https://dejandayoff.com/) at [Offensive Security](https://www.offsec.com/) for responsibly reporting this vulnerability. 

### For More Information 

View the NeuVector [Security Policy](https://github.com/neuvector/neuvector/security) 

General NeuVector [documentation](https://open-docs.neuvector.com/)

## References
- https://github.com/neuvector/neuvector/security/advisories/GHSA-622h-h2p8-743x
- https://nvd.nist.gov/vuln/detail/CVE-2023-32188
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-32188
- https://github.com/neuvector/neuvector
- https://open-docs.neuvector.com/releasenotes/5x
