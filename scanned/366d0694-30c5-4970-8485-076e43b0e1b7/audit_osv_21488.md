# [C] CVE-2021-43445

## Summary
Severity: Critical
Advisory: CVE-2021-43445
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-23
Source: https://osv.dev/vulnerability/CVE-2021-43445
Type: osv

## Details
ONLYOFFICE all versions as of 2021-11-08 is affected by Incorrect Access Control. An attacker can authenticate with the web socket service of the ONLYOFFICE document editor which is protected by JWT auth by using a default JWT signing key.

## References
- https://github.com/ONLYOFFICE/server
- https://labs.nettitude.com/blog/exploiting-onlyoffice-web-sockets-for-unauthenticated-remote-code-execution/
- https://www.onlyoffice.com/
