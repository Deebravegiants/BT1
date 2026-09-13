# [H] CVE-2023-45931

## Summary
Severity: High
Advisory: CVE-2023-45931
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-45931
Type: osv

## Details
Mesa 23.0.4 was discovered to contain a NULL pointer dereference in check_xshm() for the has_error state. NOTE: this is disputed because there is no scenario in which the vulnerability was demonstrated.

## References
- http://packetstormsecurity.com/files/176813/Mesa-23.0.4-Null-Pointer.html
- http://seclists.org/fulldisclosure/2024/Jan/59
- http://seclists.org/fulldisclosure/2024/Jan/71
- https://seclists.org/fulldisclosure/2024/Jan/71
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45931.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-45931
- https://gitlab.freedesktop.org/mesa/mesa/-/issues/9859
