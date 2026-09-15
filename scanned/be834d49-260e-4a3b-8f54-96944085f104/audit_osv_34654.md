# [H] CVE-2025-63391

## Summary
Severity: High
Advisory: CVE-2025-63391
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-63391
Type: osv

## Details
An authentication bypass vulnerability exists in Open-WebUI <=0.6.32 in the /api/config endpoint. The endpoint lacks proper authentication and authorization controls, exposing sensitive system configuration data to unauthenticated remote attackers.

## References
- https://gist.github.com/Cristliu/889471313b3c698fff74d32b7717807c
- https://gist.github.com/Cristliu/13c41b97285b776275bc8bfd3504e51b
- https://github.com/open-webui/open-webui/issues
