# [M] DSPy 3.3.0b1 Local File Read via Image/Audio Output Field Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-72742
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72742
Type: osv

## Details
DSPy 3.3.0b1 contains a file exfiltration vulnerability in the Image and Audio output field adapters that allows attackers with influence over language model outputs to read arbitrary local files by injecting a filesystem path into the url field of a parsed Image or Audio typed output. The JSONAdapter and ChatAdapter parse untrusted language model completions through parse_value into TypeAdapter validation, which triggers encode_image or encode_audio to read and base64-encode any local file path via the os.path.isfile branch in image.py and audio.py, subsequently embedding the file contents into outgoing prompt messages sent to the attacker-controlled model endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72742.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72742
- https://www.vulncheck.com/advisories/dspy-0b1-local-file-read-via-image-audio-output-field-parsing
- https://github.com/stanfordnlp/dspy/issues/10067
- https://github.com/stanfordnlp/dspy/commit/c69136b29aca4c00ca6da7667f7b80783188980e
- https://github.com/stanfordnlp/dspy
