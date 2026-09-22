# [H] Fickling MLAllowlist analysis pass rendered inoperative by shared mutable state in AnalysisContext.shorten_code()

## Summary
Severity: High
Advisory: CVE-2026-14535
Aliases: GHSA-cffv-grgg-g429, PYSEC-2026-2150
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2026-14535
Type: osv

## Details
In Trail of Bits fickling versions up to and including 0.1.11, the UnsafeImportsML analysis pass unconditionally calls AnalysisContext.shorten_code(node) on every import node it inspects, regardless of whether the import is flagged as unsafe. This call registers the shortened code representation in the shared AnalysisContext.reported_shortened_code set. When the MLAllowlist analysis pass subsequently runs, it calls the same shorten_code() method, receives already_reported=True for every import, and executes a continue statement that skips its allowlist check entirely. This renders MLAllowlist dead code for all imports — it never evaluates whether an import is in the ML allowlist or not. The MLAllowlist pass was designed to catch imports of modules outside the known-safe ML ecosystem (torch, numpy, transformers, etc.) that slip past the UnsafeImports denylist. With MLAllowlist inoperative, any standard library module not in the UNSAFE_IMPORTS denylist can be invoked via pickle deserialization while fickling's check_safety() returns LIKELY_SAFE. The fickling.load() API chains check_safety() into pickle.loads() as an explicit security gate, meaning a LIKELY_SAFE verdict causes the payload to be deserialized and executed. The root cause is shared mutable state between independently-correct analysis passes — UnsafeImportsML works as designed in isolation, MLAllowlist works as designed in isolation, but the shared reported_shortened_code set causes UnsafeImportsML to poison MLAllowlist's deduplication logic.

## References
- https://github.com/trailofbits/fickling/releases/tag/v0.1.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14535.json
- https://github.com/trailofbits/fickling/security/advisories/GHSA-cffv-grgg-g429
- https://nvd.nist.gov/vuln/detail/CVE-2026-14535
- https://github.com/trailofbits/fickling/commit/41ce7cb01edd97072994039574a2301ebb3f463d
- https://github.com/trailofbits/fickling/pull/278
- https://pypi.org/project/fickling/
