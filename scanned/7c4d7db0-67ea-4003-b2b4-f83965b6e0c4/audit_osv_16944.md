# [C] CVE-2020-10788

## Summary
Severity: Critical
Advisory: CVE-2020-10788
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-10788
Type: osv

## Details
openITCOCKPIT before 3.7.3 uses the 1fea123e07f730f76e661bced33a94152378611e API key rather than generating a random API Key for WebSocket connections.

## References
- https://openitcockpit.io/2020/2020/03/23/openitcockpit-3-7-3-released/
- https://github.com/it-novum/openITCOCKPIT/commit/581cc9007bbfba84a2575729d5d903ab3a8f25ee
