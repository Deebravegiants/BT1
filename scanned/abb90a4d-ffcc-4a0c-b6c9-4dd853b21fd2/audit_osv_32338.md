# [C] Applio allows unsafe deserialization in inference.py

## Summary
Severity: Critical
Advisory: CVE-2025-27781
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-19
Source: https://osv.dev/vulnerability/CVE-2025-27781
Type: osv

## Details
Applio is a voice conversion tool. Versions 3.2.8-bugfix and prior are vulnerable to unsafe deserialization in inference.py. `model_file` in inference.py as well as `model_file` in tts.py take user-supplied input (e.g. a path to a model) and pass that value to the `change_choices` and later to `get_speakers_id` function, which loads that model with `torch.load` in inference.py (line 326 in 3.2.8-bugfix), which is vulnerable to unsafe deserialization. The issue can lead to remote code execution. A patch is available on the `main` branch of the repository.

## References
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/inference/inference.py#L325
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/inference/inference.py#L338-L345
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/tts/tts.py#L50-L57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27781.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27781
- https://securitylab.github.com/advisories/GHSL-2024-341_GHSL-2024-353_Applio/
- https://github.com/IAHispano/Applio/commit/eb21d9dd349a6ae1a28c440b30d306eafba65097
