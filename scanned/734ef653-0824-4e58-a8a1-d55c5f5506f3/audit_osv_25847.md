# [M] CVE-2023-45922

## Summary
Severity: Medium
Advisory: CVE-2023-45922
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-45922
Type: osv

## Details
glx_pbuffer.c in Mesa 23.0.4 was discovered to contain a segmentation violation when calling __glXGetDrawableAttribute(). NOTE: this is disputed because there are no common situations in which users require uninterrupted operation with an attacker-controller server.

## References
- http://packetstormsecurity.com/files/176805/Mesa-23.0.4-Buffer-Overflow-Null-Pointer.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45922.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-45922
- https://gitlab.freedesktop.org/mesa/mesa/-/issues/9857
- http://seclists.org/fulldisclosure/2024/Jan/50
- http://seclists.org/fulldisclosure/2024/Jan/71
