# [H] Applio allows SSRF and file write in model_download.py

## Summary
Severity: High
Advisory: CVE-2025-27774
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-19
Source: https://osv.dev/vulnerability/CVE-2025-27774
Type: osv

## Details
Applio is a voice conversion tool. Versions 3.2.7 and prior are vulnerable to server-side request forgery (SSRF) and file write in `model_download.py` (line 156 in 3.2.7). The blind SSRF allows for sending requests on behalf of Applio server and can be leveraged to probe for other vulnerabilities on the server itself or on other back-end systems on the internal network, that the Applio server can reach. The blind SSRF can also be coupled with the an arbitrary file read (e.g., CVE-2025-27784) to read files from hosts on the internal network, that the Applio server can reach, which would make it a full SSRF. The file write allows for writing files on the server, which can be coupled with other vulnerabilities, for example an unsafe deserialization, to achieve remote code execution on the Applio server. As of time of publication, no known patches are available.

## References
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/assets/flask/routes.py#L14
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/rvc/lib/tools/model_download.py#L143
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/rvc/lib/tools/model_download.py#L147-L148
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/download/download.py#L192-L196
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27774.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27774
- https://securitylab.github.com/advisories/GHSL-2024-341_GHSL-2024-353_Applio/
