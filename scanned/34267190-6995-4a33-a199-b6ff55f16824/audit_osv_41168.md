# [C] LLaMA-Factory 0.9.5 Remote Code Execution via WebUI Model Path

## Summary
Severity: Critical
Advisory: CVE-2026-58116
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58116
Type: osv

## Details
LLaMA-Factory through 0.9.5 contains a remote code execution vulnerability that allows attackers with WebUI access to execute arbitrary Python code by supplying a malicious model path in the Chat or Training interfaces. The application passes user-supplied model path input unvalidated into AutoTokenizer.from_pretrained() and AutoModel.from_pretrained() with a hardcoded trust_remote_code=True parameter, causing the Hugging Face transformers library to fetch and execute arbitrary code from a remote or local model repository with the privileges of the server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58116.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58116
- https://www.vulncheck.com/advisories/llama-factory-remote-code-execution-via-webui-model-path
- https://github.com/hiyouga/LlamaFactory
- https://gist.github.com/henrrrychau/08d76ec672f42136bbc1449c4f2973f8
