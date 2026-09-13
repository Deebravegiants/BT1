# [M] Missing Authentication Allows Unauthorized Creation of Crypto Groups in RansomLook

## Summary
Severity: Medium
Advisory: CVE-2026-78369
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:L/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78369
Type: osv

## Details
RansomLook contains a missing authentication vulnerability in the /admin/crypto/group/new endpoint. While the endpoint provides an administrative function for creating new crypto group entries, it was not protected by the application's authentication mechanism.

An unauthenticated remote attacker able to access the RansomLook web interface could therefore submit requests to this endpoint and create crypto group entries without possessing a valid authenticated session or administrative credentials.

Successful exploitation allows an attacker to make unauthorized modifications to data that should only be manageable by authenticated administrators. Depending on how crypto group information is subsequently consumed by RansomLook, malicious or fraudulent entries could also affect the integrity of information presented or processed by the application.

The vulnerability is addressed by applying the flask_login.login_required decorator to the /admin/crypto/group/new route, ensuring that only authenticated users can access the functionality.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78369.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78369
- https://github.com/RansomLook/RansomLook/commit/fc25bc4f3d42d3440f9760702c3a5be138bc56a3
- https://github.com/RansomLook/RansomLook
