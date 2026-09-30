# [C] ComfyUI 0.23.0 Unauthenticated RCE via LoadTrainingDataset Pickle Deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-68771
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-68771
Type: osv

## Details
ComfyUI v0.23.0 contains an unsafe deserialization vulnerability in the LoadTrainingDataset node that allows unauthenticated remote attackers to execute arbitrary Python code by uploading a crafted pickle file and triggering its deserialization. Attackers can upload a malicious shard_*.pkl file via the unauthenticated POST /upload/image endpoint and then queue a workflow graph via POST /prompt referencing the uploaded file, causing torch.load to deserialize the attacker-controlled pickle payload using __reduce__ and execute arbitrary commands as the ComfyUI process user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68771.json
- https://github.com/Comfy-Org/ComfyUI/pull/14543
- https://nvd.nist.gov/vuln/detail/CVE-2026-68771
- https://www.vulncheck.com/advisories/comfyui-unauthenticated-rce-via-loadtrainingdataset-pickle-deserialization
- https://github.com/Comfy-Org/ComfyUI/commit/94ee49b1612824366a8631ea069b2a1fa5c73720
- https://github.com/Comfy-Org/ComfyUI
