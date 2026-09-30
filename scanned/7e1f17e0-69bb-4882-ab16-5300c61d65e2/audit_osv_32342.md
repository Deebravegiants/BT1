# [H] Applio allows arbitrary file removal in core.py

## Summary
Severity: High
Advisory: CVE-2025-27786
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-19
Source: https://osv.dev/vulnerability/CVE-2025-27786
Type: osv

## Details
Applio is a voice conversion tool. Versions 3.2.8-bugfix and prior are vulnerable to arbitrary file removal in core.py. `output_tts_path` in tts.py takes arbitrary user input and passes it to `run_tts_script` function in core.py, which checks if the path in `output_tts_path` exists, and if yes, removes that path, which leads to arbitrary file removal. As of time of publication, no known patches are available.

## References
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/core.py#L329
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/tts/tts.py#L133
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27786.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27786
- https://securitylab.github.com/advisories/GHSL-2024-341_GHSL-2024-353_Applio/
