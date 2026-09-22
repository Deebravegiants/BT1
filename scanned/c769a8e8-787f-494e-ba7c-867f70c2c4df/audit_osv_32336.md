# [C] Applio allows unsafe deserialization in model_blender.py

## Summary
Severity: Critical
Advisory: CVE-2025-27779
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-19
Source: https://osv.dev/vulnerability/CVE-2025-27779
Type: osv

## Details
Applio is a voice conversion tool. Versions 3.2.8-bugfix and prior are vulnerable to unsafe deserialization in `model_blender.py` lines 20 and 21. `model_fusion_a` and `model_fusion_b` from voice_blender.py take user-supplied input (e.g. a path to a model) and pass that value to the `run_model_blender_script` and later to `model_blender` function, which loads these two models with `torch.load` in `model_blender.py (on lines 20-21 in 3.2.8-bugfix), which is vulnerable to unsafe deserialization. The issue can lead to remote code execution. A patch is available on the `main` branch of the Applio repository.

## References
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/rvc/train/process/model_blender.py#L20-L21
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/voice_blender/voice_blender.py#L39-L56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27779.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27779
- https://securitylab.github.com/advisories/GHSL-2024-341_GHSL-2024-353_Applio/
- https://github.com/IAHispano/Applio/commit/11d139508d615a6db4d48b76634a443c66170dda
