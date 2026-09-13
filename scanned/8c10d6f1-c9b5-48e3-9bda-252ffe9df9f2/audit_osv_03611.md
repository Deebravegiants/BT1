# [M] ALPINE-CVE-2026-33948

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33948
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33948
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. Commits before 6374ae0bcdfe33a18eb0ae6db28493b1f34a0a5b contain a vulnerability where CLI input parsing allows validation bypass via embedded NUL bytes. When reading JSON from files or stdin, jq uses strlen() to determine buffer length instead of the actual byte count from fgets(), causing it to truncate input at the first NUL byte and parse only the preceding prefix. This enables an attacker to craft input with a benign JSON prefix before a NUL byte followed by malicious trailing data, where jq validates only the prefix as valid JSON while silently discarding the suffix. Workflows relying on jq to validate untrusted JSON before forwarding it to downstream consumers are susceptible to parser differential attacks, as those consumers may process the full input including the malicious trailing bytes. This issue has been patched by commit 6374ae0bcdfe33a18eb0ae6db28493b1f34a0a5b.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33948
