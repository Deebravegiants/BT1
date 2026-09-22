# [M] LangChain: Path traversal and sandbox escape in LangChain file-search middleware and loaders

## Summary
Severity: Medium
Advisory: GHSA-gr75-jv2w-4656
CVE: CVE-2026-55443
CWE: CWE-22, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-gr75-jv2w-4656
Type: github-advisory

## Affected
- PyPI: `langchain` — affected >=0 <1.3.9
- PyPI: `langchain-anthropic` — affected >=0 <1.4.6

## Details
## Summary

Several LangChain components that resolve filesystem paths or expand search patterns do not consistently confine the *resolved* path to the intended root directory. Affected behaviors include: a file-search agent middleware that validates a starting directory but not the search pattern or the resolved target of matched files, so glob patterns and symlinks can reach files outside the configured root; prompt- and chain/agent-configuration loaders that accept path fields and resolve them without confining the result to a trusted base or rejecting symlink targets; and path-prefix authorization checks that compare by string prefix without a path-segment boundary, so a sibling path sharing the prefix is accepted. When these components receive path values, search patterns, or workspace contents influenced by an untrusted source — including an LLM acting on untrusted input — the result can be disclosure of files outside the intended boundary. We have no evidence of this behavior being triggered in the wild.

## Affected users / systems

You may be affected if you expose an agent with filesystem-search middleware over a directory and accept prompts or retrieved content influenced by untrusted sources; load prompt or chain/agent configuration from untrusted or shared sources; or rely on path-prefix restrictions to confine tool file access. Callers that confine these components to fully trusted inputs and first-party configuration are not affected.

## Impact

- Confidentiality: disclosure of file contents outside the intended root/sandbox.
- Authorization: path-prefix bypass can grant access to sibling resources beyond the intended subtree.

## Patches / mitigation

The affected components will canonicalize candidate paths (resolving symlinks) and verify the resolved real path remains within the configured root before reading or returning it; search patterns will be normalized so they cannot escape the root; configuration loaders will confine resolved path fields and reject symlink escapes unless the caller explicitly opts in to dangerous loading; and path-prefix checks will enforce a path-segment boundary. Path validation will be made operating-system-portable.

## Compatibility

Callers that already pass only in-root paths, validated configuration, and trusted search inputs see no behavioral change. Callers that intentionally reference external paths can opt in via the existing dangerous-loading flag.

## Operational guidance

Confine filesystem-backed agent tools to a dedicated directory and prefer running them sandboxed/containerized; validate path and identifier inputs where untrusted input enters; do not enable dangerous loading for configuration whose origin you do not control.

## LangSmith / hosted deployments note

This issue concerns library components executed by agents.

## References
- https://github.com/langchain-ai/langchain/security/advisories/GHSA-gr75-jv2w-4656
- https://nvd.nist.gov/vuln/detail/CVE-2026-55443
- https://github.com/langchain-ai/langchain/commit/dcaf7795a3e6590af55c3ff7bda6add6355e9ea6
- https://github.com/langchain-ai/langchain
