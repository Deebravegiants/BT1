# [M] BunkerWeb has Open Redirect Vulnerability in Loading Page

## Summary
Severity: Medium
Advisory: GHSA-q9rr-h3hx-m87g
CVE: CVE-2024-53264
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-q9rr-h3hx-m87g
Type: github-advisory

## Affected
- Go: `github.com/bunkerity/bunkerweb` — affected >=0 <1.5.11

## Details
### Summary:
A open redirect vulnerability exists in the loading endpoint, allowing attackers to redirect authenticated users to arbitrary external URLs via the "next" parameter.

### Details:
The loading endpoint accepts and uses an unvalidated "next" parameter for redirects:

### PoC:
Visit: `/loading?next=https://google.com` while authenticated. The page will redirect to google.com.

### Impact:
This vulnerability could be used in phishing attacks by redirecting users from a legitimate application URL to malicious sites.

## References
- https://github.com/bunkerity/bunkerweb/security/advisories/GHSA-q9rr-h3hx-m87g
- https://nvd.nist.gov/vuln/detail/CVE-2024-53264
- https://github.com/bunkerity/bunkerweb
