# [H] CVE-2021-40904

## Summary
Severity: High
Advisory: CVE-2021-40904
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-40904
Type: osv

## Details
The web management console of CheckMK Raw Edition (versions 1.5.0 to 1.6.0) allows a misconfiguration of the web-app Dokuwiki (installed by default), which allows embedded php code. As a result, remote code execution is achieved. Successful exploitation requires access to the web management interface, either with valid credentials or with a hijacked session by a user with the role of administrator.

## References
- https://github.com/Edgarloyola/CVE-2021-40904
