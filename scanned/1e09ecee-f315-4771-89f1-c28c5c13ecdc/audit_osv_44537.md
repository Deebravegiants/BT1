# [C] ModelScope through 1.40.0 Unsafe YAML Deserialization in Model Config Loading

## Summary
Severity: Critical
Advisory: CVE-2026-84202
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84202
Type: osv

## Details
ModelScope uses PyYAML's unsafe yaml.Loader to parse model configuration files, allowing arbitrary code execution through Python object construction tags. Attackers can craft malicious model repositories with poisoned configuration files that execute code when loaded by users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84202.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84202
- https://www.vulncheck.com/advisories/modelscope-through-1.40.0-unsafe-yaml-deserialization-in-model-config-loading
- https://github.com/modelscope/modelscope/issues/1660
- https://github.com/modelscope/modelscope
- https://pypi.org/project/modelscope/
- https://github.com/modelscope/modelscope/blob/v1.40.0/modelscope/models/audio/tts/voice.py
- https://github.com/modelscope/modelscope/blob/v1.40.0/modelscope/models/multi_modal/mplug/configuration_mplug.py
