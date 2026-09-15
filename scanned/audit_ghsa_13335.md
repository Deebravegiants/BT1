# [H] 1Panel command injection vulnerability in Firewall ip functionality

## Summary
Severity: High
Advisory: GHSA-p9xf-74xh-mhw5
CVE: CVE-2023-37477
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-18
Source: https://github.com/advisories/GHSA-p9xf-74xh-mhw5
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=0 <1.4.3

## Details
### Summary
An OS command injection vulnerability exists in 1Panel firewall functionality. A specially-crafted HTTP request can lead to arbitrary command execution. An attacker can make an authenticated HTTP request to trigger this vulnerability.

### Details
1Panel firewall functionality `/hosts/firewall/ip` endpoint read user input without validation, the attacker extends the default functionality of the application, which execute system commands.

### PoC
the payload `; sleep 3 #` will lead server response in 3 seconds 
![image](https://user-images.githubusercontent.com/4935500/252299676-bc4a8b92-e475-40ee-a92a-fec9fad7a6c3.png)

the payload `; sleep 6 #` will lead server response in 6 seconds 
![image](https://user-images.githubusercontent.com/4935500/252299871-766cc411-69e5-4c6c-b4ff-7774fa974ea0.png)

### Impact
An attacker can execute arbitrary code on the target system, which can lead to a complete compromise of the system.

### Patches

The vulnerability has been fixed in v1.4.3.

### Workarounds

It is recommended to upgrade the version to v1.4.3.

### References

If you have any questions or comments about this advisory:

Open an issue in https://github.com/1Panel-dev/1Panel
Email us at wanghe@fit2cloud.com

## References
- https://github.com/1Panel-dev/1Panel/security/advisories/GHSA-p9xf-74xh-mhw5
- https://nvd.nist.gov/vuln/detail/CVE-2023-37477
- https://github.com/1Panel-dev/1Panel/commit/e17b80cff4975ee343568ff526b62319f499005d
- https://github.com/1Panel-dev/1Panel
- https://github.com/1Panel-dev/1Panel/releases/tag/v1.4.3
