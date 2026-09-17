# [M] LangGraph checkpoint loading has unsafe msgpack deserialization

## Summary
Severity: Medium
Advisory: GHSA-g48c-2wqr-h844
CVE: CVE-2026-28277
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-g48c-2wqr-h844
Type: github-advisory

## Affected
- PyPI: `langgraph` — affected >=0 <1.0.10

## Details
LangGraph checkpointers can load msgpack-encoded checkpoints that reconstruct Python objects during deserialization. If an attacker can modify checkpoint data in the backing store (for example, after a database compromise or other privileged write access to the persistence layer), they can potentially supply a crafted payload that triggers unsafe object reconstruction when the checkpoint is loaded.

This is a **post-exploitation / defense-in-depth** issue. Exploitation requires the ability to write attacker-controlled checkpoint bytes at rest. In most deployments that prerequisite already implies a serious incident; the additional risk is turning “checkpoint-store write access” into code execution in the application runtime, which can expand blast radius (for example by exposing environment variables or cloud credentials available to the runtime).

There is no evidence of exploitation in the wild, and LangGraph is not aware of a practical exploitation path in existing deployments today. This change is intended to reduce the blast radius of a checkpoint-store compromise.

## Affected users / systems

Users may be affected if they:

- use a persistent checkpointer (database, remote store, shared filesystem, etc.),
- load/resume from checkpoints, and
- operate in an environment where an attacker could gain privileged write access to checkpoint data in the backing store.

This issue requires the attacker to be able to modify persisted checkpoint bytes (or to compromise a trusted component that writes them). It is generally not reachable by an unauthenticated remote attacker in a correctly configured deployment.

## Impact
- Potential **arbitrary code execution** or other unsafe side effects during checkpoint deserialization.
- Escalation from “write access to checkpoint store” to “code execution in the application runtime,” which may expose runtime secrets or provide access to other systems the runtime can reach.

## Exploitation scenario (high level)
1. Attacker gains privileged write access to the checkpoint store (for example, via database compromise, leaked credentials, or abuse of an administrative data path).
2. Attacker writes a crafted checkpoint payload containing msgpack data intended to reconstruct dangerous objects.
3. Application resumes and deserializes the checkpoint; unsafe reconstruction could execute attacker-controlled behavior.

## Mitigation / remediation
LangGraph provides an allowlist-based hardening mechanism for msgpack checkpoint deserialization.

### Strict mode (environment variable)
- **`LANGGRAPH_STRICT_MSGPACK`**
  - When set truthy (`1`, `true`, `yes`), the default msgpack deserialization policy becomes strict.
  - Concretely: `JsonPlusSerializer()` will default `allowed_msgpack_modules` to `None` (strict) instead of `True` (warn-and-allow), unless `allowed_msgpack_modules=...` is explicitly passed.

### `allowed_msgpack_modules` (serializer/checkpointer config)
This setting controls what msgpack “ext” types are allowed to be reconstructed.

- `True` (default when strict mode is not enabled): allow all ext types, but log a warning when deserializing a type that is not explicitly registered.
- `None` (strict): only a built-in safe set is reconstructed; other ext types are blocked.
- `[(module, class_name), ...]` (strict allowlist): the built-in safe set plus exactly the listed symbols are reconstructed (exact-match).

### Built-in safe set
A small set of types is always treated as safe to reconstruct (for example `datetime` types, `uuid.UUID`, `decimal.Decimal`, `set`/`frozenset`/`deque`, `ipaddress` types, `pathlib` paths, `zoneinfo.ZoneInfo`, compiled regex patterns, and selected LangGraph internal types).

### Automatically derived allowlist (only when compiling graphs)
When `LANGGRAPH_STRICT_MSGPACK` is enabled and `StateGraph` is compiled, LangGraph derives an allowlist from the graph’s schemas and channels and applies it to the checkpointer.

- The allowlist is built by walking the state/input/output/context schemas (plus node/branch input schemas) and channel value/update types. It includes Pydantic v1/v2 models, dataclasses, enums, TypedDict field types, and common typing constructs (containers, unions, `Annotated`).
- LangGraph also includes a curated set of common LangChain message classes.

This derived allowlist is only applied if the selected checkpointer supports `with_allowlist(...)`. If a user is constructing serializers/checkpointers manually (or using a checkpointer that does not support allowlist propagation), they will need to configure `allowed_msgpack_modules` themselves.

### Operational guidance
- Treat checkpoint stores as integrity-sensitive. Restrict write access and rotate credentials if compromise is suspected.
- Enable strict mode (`LANGGRAPH_STRICT_MSGPACK=true`) in production if feasible, and rely on schema-driven allowlisting to reduce incompatibilities.
- Avoid providing custom msgpack deserialization hooks that reconstruct arbitrary types unless checkpoint data is fully trusted.

## Limitations / important notes
- If a checkpointer implementation does **not** support allowlist application (i.e., does not implement `with_allowlist`), allowlist enforcement may be skipped (with a warning). In that situation, strict expectations may not hold.
- If an application supplies a custom msgpack unpack hook (`ext_hook`), the custom hook controls reconstruction and can bypass the default allowlist checks (intentional escape hatch, but it weakens the protection).

## LangSmith / hosted deployments note
LangSmith is not aware of this issue presenting risk to existing LangSmith-hosted deployments. The described threat model requires an attacker to tamper with the checkpoint persistence layer used by the deployment; typical hosted configurations are designed to prevent such access.

First reported by:  yardenporat353

## References
- https://github.com/langchain-ai/langgraph/security/advisories/GHSA-g48c-2wqr-h844
- https://nvd.nist.gov/vuln/detail/CVE-2026-28277
- https://github.com/langchain-ai/langgraph
- https://github.com/pypa/advisory-database/tree/main/vulns/langgraph/PYSEC-2026-83.yaml
