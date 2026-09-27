# [C] SpeechBrain < 1.1.1 Arbitrary Code Execution via CKPT.yaml Parsing

## Summary
Severity: Critical
Advisory: CVE-2026-10036
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-10036
Type: osv

## Details
SpeechBrain before 1.1.1 contains an arbitrary code execution vulnerability that allows attackers to execute arbitrary code by supplying a crafted CKPT.yaml checkpoint metadata file parsed with PyYAML's unsafe loader during candidate enumeration in Checkpointer.recover_if_possible(). Attackers can embed malicious Python object construction tags such as !!python/object/apply in any CKPT.yaml file within the configured checkpoint path to trigger code execution during candidate discovery, even if the malicious checkpoint is never selected for recovery.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10036.json
- https://github.com/speechbrain/speechbrain/releases/tag/v1.1.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-10036
- https://www.vulncheck.com/advisories/speechbrain-arbitrary-code-execution-via-ckpt-yaml-parsing
- https://github.com/speechbrain/speechbrain/commit/22a616646a493871401461f80b2d5cf564cb2850
- https://github.com/speechbrain/speechbrain/pull/3067
- https://github.com/speechbrain/speechbrain
- https://github.com/SaiTeja-Erukude/CVE-2026-10036-speechbrain-rce
