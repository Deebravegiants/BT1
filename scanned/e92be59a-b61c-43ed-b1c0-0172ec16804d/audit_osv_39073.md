# [M] F5-TTS 1.1.20 Path Traversal via finetune_gradio.py create_data_project()

## Summary
Severity: Medium
Advisory: CVE-2026-43624
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-43624
Type: osv

## Details
F5-TTS through version 1.1.20 contains a path traversal vulnerability in the finetune Gradio handlers that allows unauthenticated attackers to write arbitrary files by passing unsanitized user-supplied project names directly to os.path.join() without validating the resulting path stays within the intended base directory. Attackers can supply absolute path arguments such as /tmp/EVIL to override the base directory entirely and create arbitrary directories with attacker-controlled JSON content at any filesystem path writable by the server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43624.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43624
- https://www.vulncheck.com/advisories/f5-tts-path-traversal-via-finetune-gradio-py-create-data-project
- https://github.com/SWivid/F5-TTS/issues/1293
- https://github.com/SWivid/F5-TTS/pull/1294
- https://github.com/SWivid/F5-TTS/commit/2f53ded68e5f69e248ceb200a51ef4d1dc647936
- https://github.com/SWivid/F5-TTS
