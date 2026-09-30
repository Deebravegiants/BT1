# [C] whichllm < 0.5.16 Code Injection via run and snippet commands

## Summary
Severity: Critical
Advisory: CVE-2026-58474
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-58474
Type: osv

## Details
whichllm before 0.5.16 contains a code injection vulnerability in the run and snippet commands that allows a remote attacker who controls a HuggingFace repository to achieve arbitrary code execution by crafting a malicious GGUF filename containing double quotes or other special characters. The script generation function in cli.py interpolates HuggingFace-derived values, including GGUF variant filenames from the Hub API siblings rfilename field, directly into Python source code without escaping, allowing the crafted filename to break out of the generated string literal and execute injected code on the user's machine before any model download occurs.

## References
- https://github.com/Andyyyy64/whichllm/releases/tag/v0.5.16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58474.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58474
- https://www.vulncheck.com/advisories/whichllm-code-injection-via-run-and-snippet-commands
- https://github.com/Andyyyy64/whichllm/commit/77e8dc9e8b45212c694d631d758623e17a00859e
- https://github.com/Andyyyy64/whichllm/pull/147
- https://github.com/Andyyyy64/whichllm
