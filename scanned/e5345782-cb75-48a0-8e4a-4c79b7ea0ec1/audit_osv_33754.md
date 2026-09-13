# [C] GHSL-2025-049: GPT-SoVITS Deserialization of Untrusted Data vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-49837
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2025-49837
Type: osv

## Details
GPT-SoVITS-WebUI is a voice conversion and text-to-speech webUI. In versions 20250228v3 and prior, there is an unsafe deserialization vulnerability in vr.py AudioPre. The model_choose variable takes user input (e.g. a path to a model) and passes it to the uvr function. In uvr, a new instance of AudioPre class is created with the model_path attribute containing the aforementioned user input (here called locally model_name). Note that in this step the .pth extension is added to the path. In the AudioPre class, the user input, here called model_path, is used to load the model on that path with torch.load, which can lead to unsafe deserialization. At time of publication, no known patched versions are available.

## References
- https://github.com/RVC-Boss/GPT-SoVITS/blob/165882d64f474b3563fa91adc1a679436ae9c3b8/tools/uvr5/vr.py#L32
- https://github.com/RVC-Boss/GPT-SoVITS/blob/165882d64f474b3563fa91adc1a679436ae9c3b8/tools/uvr5/webui.py#L157
- https://github.com/RVC-Boss/GPT-SoVITS/blob/165882d64f474b3563fa91adc1a679436ae9c3b8/tools/uvr5/webui.py#L192-L205
- https://github.com/RVC-Boss/GPT-SoVITS/blob/165882d64f474b3563fa91adc1a679436ae9c3b8/tools/uvr5/webui.py#L64-L70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49837.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49837
- https://securitylab.github.com/advisories/GHSL-2025-049_GHSL-2025-053_RVC-Boss_GPT-SoVITS/
