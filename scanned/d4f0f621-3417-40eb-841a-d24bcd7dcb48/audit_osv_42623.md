# [C] sentence-transformers Arbitrary Code Execution on Local Model Load Despite trust_remote_code=False

## Summary
Severity: Critical
Advisory: CVE-2026-68770
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-68770
Type: osv

## Details
sentence-transformers contains a security control bypass vulnerability that allows attackers to achieve arbitrary code execution by exploiting a logic flaw in the import_module_class helper within sentence_transformers/util/misc.py, where the guard condition includes an 'or os.path.exists(model_name_or_path)' clause that satisfies the trust gate whenever the supplied path exists on the local filesystem, regardless of the trust_remote_code=False argument. Attackers who can control or influence the contents of a model directory on disk can place malicious Python files such as modeling_*.py referenced via modules.json, causing the code to execute at import time when an application loads the model with SentenceTransformer(path, trust_remote_code=False), bypassing the documented security contract and achieving code execution within the loading process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68770.json
- https://github.com/huggingface/sentence-transformers/pull/3807
- https://nvd.nist.gov/vuln/detail/CVE-2026-68770
- https://www.vulncheck.com/advisories/sentence-transformers-arbitrary-code-execution-on-local-model-load-despite-trust-remote-code-false
- https://github.com/huggingface/sentence-transformers/issues/3801
- https://github.com/huggingface/sentence-transformers/commit/ae1acc3fb2aa2004577b297eb4a915ce7a03316a
- https://github.com/huggingface/sentence-transformers
