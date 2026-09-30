# [C] Silver vulnerable to MitM attack against implants due to a cryptography vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8jxm-xp43-qh3q
CVE: CVE-2023-34758
CWE: CWE-327
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-8jxm-xp43-qh3q
Type: github-advisory

## Affected
- Go: `github.com/bishopfox/sliver` — affected >=1.5.0 <1.5.40

## Details
### Summary
The current cryptography implementation in Sliver up to version 1.5.39 allows a MitM with access to the corresponding implant binary to execute arbitrary codes on implanted devices via intercepted and crafted responses. (Reserved CVE ID: CVE-2023-34758)

### Details
Please see [the PoC repo](https://github.com/tangent65536/Slivjacker).

### PoC
Please also see [the PoC repo](https://github.com/tangent65536/Slivjacker).
To setup a simple PoC environment,  
 1. Generate an implant with its C2 set to the PoC server's address and copy the embedded private implant key and public server key into the config json.  
 2. Run the implant on a separate VM and a `notepad.exe` window should pop up on the implanted VM.  

### Impact
A successful attack grants the attacker permission to execute arbitrary code on the implanted device.  
  
### References
https://github.com/BishopFox/sliver/blob/master/implant/sliver/cryptography/implant.go  
https://github.com/BishopFox/sliver/blob/master/implant/sliver/cryptography/crypto.go  
https://github.com/tangent65536/Slivjacker  

### Credits
[Ting-Wei Hsieh](https://github.com/tangent65536) from [CHT Security Co. Ltd.](https://www.chtsecurity.com/?lang=en)

## References
- https://github.com/BishopFox/sliver/security/advisories/GHSA-8jxm-xp43-qh3q
- https://nvd.nist.gov/vuln/detail/CVE-2023-34758
- https://nvd.nist.gov/vuln/detail/CVE-2023-35170
- https://github.com/BishopFox/sliver/commit/2d1ea6192cac2ff9d6450b2d96043fdbf8561516
- https://github.com/BishopFox/sliver
- https://github.com/BishopFox/sliver/blob/master/implant/sliver/cryptography/crypto.go
- https://github.com/BishopFox/sliver/blob/master/implant/sliver/cryptography/implant.go
- https://github.com/BishopFox/sliver/releases/tag/v1.5.40
- https://github.com/tangent65536/Slivjacker
- https://pkg.go.dev/vuln/GO-2023-1866
- https://www.chtsecurity.com/news/04f41dcc-1851-463c-93bc-551323ad8091
