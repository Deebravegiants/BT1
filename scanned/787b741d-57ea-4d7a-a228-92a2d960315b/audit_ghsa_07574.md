# [C] EPyT-Flow vulnerable to unsafe JSON deserialization (__type__)

## Summary
Severity: Critical
Advisory: GHSA-74vm-8frp-7w68
CVE: CVE-2026-25632
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-74vm-8frp-7w68
Type: github-advisory

## Affected
- PyPI: `epyt-flow` — affected >=0 <0.16.1

## Details
### Impact
EPyT-Flow’s REST API parses attacker-controlled JSON request bodies using a custom deserializer (my_load_from_json) that supports a __type__ field. When __type__ is present, the deserializer dynamically imports an attacker-specified module/class and instantiates it with attacker-supplied arguments. This allows invoking dangerous classes such as subprocess.Popen, which can lead to OS command execution during JSON parsing. This also affects the loading of JSON files.

### Patches
EPyT-Flow  has been patched in 0.16.1 -- affects all versions <= 0.16.0

### Workarounds
Do not load any JSON from untrusted sources and do not expose the REST API.

### Credits
EPyT-Flow  thanks Jarrett Chan (@syphonetic) for detecting and reporting the bug.

## References
- https://github.com/WaterFutures/EPyT-Flow/security/advisories/GHSA-74vm-8frp-7w68
- https://nvd.nist.gov/vuln/detail/CVE-2026-25632
- https://github.com/WaterFutures/EPyT-Flow/commit/3fff9151494c7dbc72073830b734f0a7e550e385
- https://github.com/WaterFutures/EPyT-Flow
- https://github.com/WaterFutures/EPyT-Flow/releases/tag/v0.16.1
