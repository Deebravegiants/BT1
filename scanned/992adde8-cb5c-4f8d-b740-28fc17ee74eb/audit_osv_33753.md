# [C] GHSL-2025-045: GPT-SoVITS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-49833
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2025-49833
Type: osv

## Details
GPT-SoVITS-WebUI is a voice conversion and text-to-speech webUI. In versions 20250228v3 and prior, there is a command injection vulnerability in the webui.py open_slice function. slice_opt_root and slice-inp-path takes user input, which is passed to the open_slice function, which concatenates the user input into a command and runs it on the server, leading to arbitrary command execution. At time of publication, no known patched versions are available.

## References
- https://github.com/RVC-Boss/GPT-SoVITS/blob/165882d64f474b3563fa91adc1a679436ae9c3b8/webui.py#L1036
- https://github.com/RVC-Boss/GPT-SoVITS/blob/165882d64f474b3563fa91adc1a679436ae9c3b8/webui.py#L501
- https://github.com/RVC-Boss/GPT-SoVITS/blob/165882d64f474b3563fa91adc1a679436ae9c3b8/webui.py#L503
- https://github.com/RVC-Boss/GPT-SoVITS/blob/165882d64f474b3563fa91adc1a679436ae9c3b8/webui.py#L889
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49833.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49833
- https://securitylab.github.com/advisories/GHSL-2025-045_GHSL-2025-048_RVC-Boss_GPT-SoVITS/
