# [C] Vocos through 0.1.0 Arbitrary Code Execution via Unrestricted class_path in Model Configuration

## Summary
Severity: Critical
Advisory: CVE-2026-79784
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79784
Type: osv

## Details
Vocos instantiates a class named by a configuration file without restricting which class may be named. instantiate_class in vocos/pretrained.py takes the class_path value from the configuration, splits it into a module and an attribute, imports the module with __import__, resolves the attribute with getattr, and calls the result as args_class(*args, **kwargs) where kwargs is the config's own init_args mapping. No allowlist constrains the dotted path, so a configuration may name any importable callable and supply the arguments it is called with. Vocos.from_hparams reaches this for each of the feature_extractor, backbone and head entries, and Vocos.from_pretrained reaches it with a remote file: it downloads config.yaml from a caller-named Hugging Face repository and passes it straight to from_hparams. Loading a model from a repository the user does not control therefore executes code of the repository owner's choosing in the loading process. The neighbouring torch.load of the downloaded weights is a separate matter and is constrained on PyTorch releases that default weights_only to true, which leaves this path as the reachable one.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79784.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-79784
- https://www.vulncheck.com/advisories/vocos-through-arbitrary-code-execution-via-unrestricted-class-path-in-model-configuration
- https://github.com/gemelo-ai/vocos/issues/76
- https://github.com/gemelo-ai/vocos
- https://pypi.org/project/vocos/
- https://github.com/gemelo-ai/vocos/blob/main/vocos/pretrained.py
