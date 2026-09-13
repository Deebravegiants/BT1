# [H] Banks: Arbitrary File Read via Path Traversal in Media Filters (image/audio/video/document)

## Summary
Severity: High
Advisory: CVE-2026-62663
Aliases: GHSA-98rr-gvc9-3cjh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-62663
Type: osv

## Details
Banks generates meaningful LLM prompts using a simple template language. In versions prior to 2.4.4, all four media filters (image, audio, video, document) in banks accept untrusted user input as file paths via Path(value) and pass them directly to open(file_path, "rb") without any path sanitization, canonicalization, or directory restriction. An attacker who controls template variables passed to a banks Prompt can use path traversal (../) to read arbitrary files accessible to the Python process—including .env files, SSH keys, cloud credentials, source code, /etc/passwd, and /etc/shadow—with the content returned base64-encoded in the rendered prompt output, making exfiltration trivial. This is particularly dangerous for applications that use banks to process user-provided template variables before sending prompts to an LLM. This issue has been fixed in version 2.4.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62663.json
- https://github.com/masci/banks/security/advisories/GHSA-98rr-gvc9-3cjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-62663
