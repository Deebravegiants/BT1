# [C] Imperative Local Command Injection allows Activity Masking

## Summary
Severity: Critical
Advisory: CVE-2024-6834
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H/E:F/RL:T/RC:C/CR:H/IR:H/AR:M/MAV:N/MAC:L/MPR:N/MUI:N/MS:C/MC:H/MI:H/MA:H)
Published: 2024-07-17
Source: https://osv.dev/vulnerability/CVE-2024-6834
Type: osv

## Details
A vulnerability in APIML Spring Cloud Gateway which leverages user privileges by unexpected signing proxied request by Zowe's client certificate. This allows access to a user to the endpoints requiring an internal client certificate without any credentials. It could lead to managing components in there and allow an attacker to handle the whole communication including user credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6834.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6834
- https://github.com/zowe/api-layer
