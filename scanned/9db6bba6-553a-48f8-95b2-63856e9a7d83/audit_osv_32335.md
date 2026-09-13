# [C] Applio allows unsafe deserialization in infer.py

## Summary
Severity: Critical
Advisory: CVE-2025-27778
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-19
Source: https://osv.dev/vulnerability/CVE-2025-27778
Type: osv

## Details
Applio is a voice conversion tool. Versions 3.2.8-bugfix and prior are vulnerable to unsafe deserialization in `infer.py`. The issue can lead to remote code execution. As of time of publication, a fix is available on the `main` branch of the Applio repository but not attached to a numbered release.

## References
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/rvc/infer/infer.py#L464
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/inference/inference.py#L338-L345
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/tts/tts.py#L50-L57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27778.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27778
- https://securitylab.github.com/advisories/GHSL-2024-341_GHSL-2024-353_Applio/
- https://github.com/IAHispano/Applio/commit/16019befdcbbff0b264a5e30785feef4b70df8d9
- https://github.com/IAHispano/Applio/commit/eb21d9dd349a6ae1a28c440b30d306eafba65097
