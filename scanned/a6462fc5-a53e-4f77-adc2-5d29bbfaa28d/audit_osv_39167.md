# [M] FastGPT: sandbox escape to RCE - code-sandbox regex /\bimport\s*\(/ is bypassable

## Summary
Severity: Medium
Advisory: CVE-2026-44287
Aliases: GHSA-f5mq-qxm4-5mvc
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44287
Type: osv

## Details
FastGPT is an AI Agent building platform. Prior to 4.15.0-beta1, the JavaScript sandbox worker at projects/code-sandbox/src/pool/worker.ts:356 blocks dynamic import() with the regex /\bimport\s*\(/.test(code). JavaScript syntax accepts a block comment between import and (; the regex matches only ASCII whitespace, and the bytes /, *, *, / are not in the \s character class. The payload import/**/("child_process") parses as a syntactically valid dynamic import that the regex does not detect. Because import() is not wrapped by the safeRequire Proxy (which only proxies require), the attacker loads child_process and calls execSync - arbitrary command execution as uid=100(sandbox) inside the sandbox container. This vulnerability is fixed in 4.15.0-beta1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44287.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-f5mq-qxm4-5mvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44287
