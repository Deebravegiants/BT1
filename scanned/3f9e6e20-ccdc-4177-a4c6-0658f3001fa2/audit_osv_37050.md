# [H] Agenta has Python Sandbox Escape, Leading to Remote Code Execution (RCE)

## Summary
Severity: High
Advisory: CVE-2026-27952
Aliases: GHSA-pmgp-2m3v-34mq, PYSEC-2026-6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27952
Type: osv

## Details
Agenta is an open-source LLMOps platform. In Agenta-API prior to version 0.48.1, a Python sandbox escape vulnerability existed in Agenta's custom code evaluator. Agenta used RestrictedPython as a sandboxing mechanism for user-supplied evaluator code, but incorrectly whitelisted the `numpy` package as safe within the sandbox. This allowed authenticated users to bypass the sandbox and achieve arbitrary code execution on the API server. The escape path was through `numpy.ma.core.inspect`, which exposes Python's introspection utilities — including `sys.modules` — thereby providing access to unfiltered system-level functionality like `os.system`. This vulnerability affects the Agenta self-hosted platform (API server), not the SDK when used as a standalone Python library. The custom code evaluator runs server-side within the API process. The issue is fixed in v0.48.1 by removing `numpy` from the sandbox allowlist. In later versions (v0.60+), the RestrictedPython sandbox was removed entirely and replaced with a different execution model.

## References
- https://github.com/Agenta-AI/agenta/security/advisories/GHSA-pmgp-2m3v-34mq
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27952.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27952
