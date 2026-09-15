# [M] X-AnyLabeling before 4.0.0-beta.9 Improper Certificate Validation in Model Downloads

## Summary
Severity: Medium
Advisory: CVE-2026-79785
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79785
Type: osv

## Details
X-AnyLabeling's model downloader disabled TLS certificate verification. download_with_retry in anylabeling/services/auto_labeling/model.py built a context with ssl._create_unverified_context() and passed it to urllib.request.urlopen, so neither the certificate chain nor the hostname was checked on any model download, and models are fetched over HTTPS from the project's release host. Any party positioned to intercept that connection could therefore answer it with content of their own choosing. The response is written to a .part file and moved into place with os.replace, and the only post-download check, safe_check_model, validates the file's format rather than its provenance: no hash or signature is compared against an expected value. For an ONNX target the substituted file passes onnx.checker.check_model and is then used for inference, so the attacker chooses the model that produces the application's annotations. For a .pth or .pt target, which the shipped SAM2 video, YOLOE, UPN and open_vision configurations use, the check worker calls torch.load without weights_only, so a substituted file is unpickled and executes code of the attacker's choosing on PyTorch releases predating the weights_only default.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79785.json
- https://github.com/CVHub520/X-AnyLabeling/releases/tag/v4.0.0-beta.9
- https://nvd.nist.gov/vuln/detail/CVE-2026-79785
- https://www.vulncheck.com/advisories/x-anylabeling-before-4.0.0-beta.9-improper-certificate-validation-in-model-downloads
- https://github.com/CVHub520/X-AnyLabeling/commit/52f7c30333f3f99711f09334d740212aa30b9958
- https://github.com/CVHub520/X-AnyLabeling
- https://pypi.org/project/x-anylabeling-cvhub/
- https://github.com/CVHub520/X-AnyLabeling/blob/v4.0.0-beta.8/anylabeling/services/auto_labeling/model.py
