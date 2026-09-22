# [C] Fujitsu OneCompression < 1.2.1 Arbitrary Code Execution via torch.load Deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-73325
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73325
Type: osv

## Details
Fujitsu Research's OneCompression library before 1.2.1 contains an unsafe deserialization vulnerability that allows attackers to execute arbitrary code by supplying a crafted model.pt checkpoint file, as QuantizedModelLoader.load_quantized_model_pt() unconditionally calls torch.load with weights_only=False, invoking Python's pickle machinery during deserialization. Attackers can embed malicious __reduce__ methods in a crafted model checkpoint to execute arbitrary Python code, including system commands, when the library loads the file from a caller-selected model directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73325.json
- https://github.com/FujitsuResearch/OneCompression/blob/main/SECURITY.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-73325
- https://www.vulncheck.com/advisories/fujitsu-onecompression-arbitrary-code-execution-via-torch-load-deserialization
- https://pypi.org/project/onecomp/1.2.1/
- https://pypi.org/project/onecomp/
