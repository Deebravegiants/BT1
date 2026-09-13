# [C] CVE-2024-21574

## Summary
Severity: Critical
Advisory: CVE-2024-21574
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/CVE-2024-21574
Type: osv

## Details
The issue stems from a missing validation of the pip field in a POST request sent to the /customnode/install endpoint used to install custom nodes which is added to the server by the extension. This allows an attacker to craft a request that triggers a pip install on a user controlled package or URL, resulting in remote code execution (RCE) on the server.

## References
- https://github.com/ltdrdata/ComfyUI-Manager/blob/ffc095a3e5acc1c404773a0510e6d055a6a72b0e/glob/manager_server.py#L798
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21574.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-21574
- https://github.com/ltdrdata/ComfyUI-Manager/commit/ffc095a3e5acc1c404773a0510e6d055a6a72b0e
