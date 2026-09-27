# [H] Diffusers: None.py Trust Remote Code Bypass

## Summary
Severity: High
Advisory: CVE-2026-44827
Aliases: GHSA-j7w6-vpvq-j3gm, PYSEC-2026-41
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44827
Type: osv

## Details
Diffusers is the a library for  pretrained diffusion models. Prior to 0.38.0, diffusers 0.37.0 allows remote code execution without the trust_remote_code=True safeguard when loading pipelines from Hugging Face Hub repositories. The _resolve_custom_pipeline_and_cls function in pipeline_loading_utils.py performs string interpolation on the custom_pipeline parameter using f"{custom_pipeline}.py". When custom_pipeline is not supplied by the user, it defaults to None, which Python interpolates as the literal string "None.py". If an attacker publishes a Hub repository containing a file named None.py with a class that subclasses DiffusionPipeline, the file is automatically downloaded and executed during a standard DiffusionPipeline.from_pretrained() call with no additional keyword arguments. The trust_remote_code check in DiffusionPipeline.download() is bypassed because it evaluates custom_pipeline is not None as False (since the kwarg was never supplied), while the downstream code path that actually loads the module resolves the None value into a valid filename. An attacker can achieve silent arbitrary code execution by publishing a malicious model repository with a None.py file and a standard-looking model_index.json that references a legitimate pipeline class name, requiring only that a victim calls from_pretrained on the repository. This vulnerability is fixed in 0.38.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44827.json
- https://github.com/huggingface/diffusers/security/advisories/GHSA-j7w6-vpvq-j3gm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44827
