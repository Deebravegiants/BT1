# [M] Lobe Chat API Key Leak

## Summary
Severity: Medium
Advisory: GHSA-p36r-qxgx-jq2v
CVE: CVE-2024-37895
CWE: CWE-200, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-p36r-qxgx-jq2v
Type: github-advisory

## Affected
- npm: `@lobehub/chat` — affected >=0 <0.162.25

## Details
### Summary

If an attacker can successfully authenticate through SSO/Access Code, they can obtain the real backend API Key by modifying the base URL to their own attack URL on the frontend and setting up a server-side request.

### Details

The attack process is described above.

![image](https://github.com/lobehub/lobe-chat/assets/36695271/df5e0c3c-af28-45c3-959f-182cc9d06680)

### PoC

Frontend:
1. Pass basic authentication (SSO/Access Code).
2. Set the Base URL to a private attack address.
3. Configure the request method to be a server-side request.
4. At the self-set attack address, retrieve the API Key information from the request headers.

Backend:
1. The LobeChat version allows setting the Base URL.
2. There is no outbound traffic whitelist.

### Impact

All community version LobeChat users using SSO/Access Code authentication, tested on version 0.162.13.

## References
- https://github.com/lobehub/lobe-chat/security/advisories/GHSA-p36r-qxgx-jq2v
- https://nvd.nist.gov/vuln/detail/CVE-2024-37895
- https://github.com/lobehub/lobe-chat
