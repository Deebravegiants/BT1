# [M] LangGraph Checkpoint: Unsafe JSON deserialization in checkpoint loading

## Summary
Severity: Medium
Advisory: GHSA-fjqc-hq36-qh5p
CVE: CVE-2026-48775
CWE: CWE-502, CWE-913
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-fjqc-hq36-qh5p
Type: github-advisory

## Affected
- PyPI: `langgraph-checkpoint` — affected >=0 <4.1.1

## Details
## Summary

LangGraph's `JsonPlusSerializer` can reconstruct Python objects from JSON checkpoint payloads. Under conditions where someone could modify checkpoint bytes at rest in the backing store, the deserialization path could reconstruct objects beyond what the application expects, which could in turn result in code execution at checkpoint load time.

This is a defense-in-depth issue. The affected behavior is reachable only when checkpoint bytes at rest in the backing store can be modified by an unauthorized party. In most deployments that prerequisite already implies a serious incident; the additional concern is turning "checkpoint-store write access" into code execution in the application runtime.

There is no evidence of this behavior being triggered in the wild, and the team is not aware of a practical path to it in existing deployments today. This change is intended to reduce the surface available after a checkpoint-store incident.

## Affected users / systems

Users may be affected if they:

- use a persistent checkpointer (database, remote store, shared filesystem, etc.) with the default `JsonPlusSerializer`,
- load/resume from checkpoints, and
- operate in an environment where write access to the checkpoint store could be obtained by an unauthorized party.

The default checkpoint serializer in all shipped checkpointer backends (`PostgresSaver`, `SqliteSaver`, and their async counterparts) is `JsonPlusSerializer`, so applications generally do not need to opt in to be in scope.

## Impact

- Potential **arbitrary code execution** or other unsafe side effects during checkpoint deserialization.
- Escalation from "write access to the checkpoint store" to "code execution in the LangGraph worker process," which may expose runtime secrets or provide access to other systems the runtime can reach.

## Patches / mitigation

The JSON deserialization path has been narrowed so that revival is restricted to default-constructor reconstruction using the args/kwargs carried in the payload. The framework's own encoder has not relied on the removed behavior for produced checkpoints since the msgpack migration, so this change does not affect freshly written checkpoints. Legacy payloads that already used the default constructor as their first option continue to revive correctly via that same path.

## Compatibility

A narrow legacy-resume regression applies to pre-October-2025 checkpoints of pydantic models where the original payload depended on a no-validation fallback factory to recover from incompatible schema evolution. After this change, such payloads return `None` from the revival path and fall through to the langchain-core reviver, which surfaces the raw dict rather than reconstructing the model.

## Operational guidance

- Treat checkpoint stores as integrity-sensitive. Restrict write access and rotate credentials if unauthorized access is suspected.
- Avoid providing custom JSON revival hooks that reconstruct arbitrary types unless checkpoint data is fully trusted.

## LangSmith / hosted deployments note

The team is not aware of this issue presenting concern for existing LangSmith-hosted deployments. The described conditions require modification of the checkpoint persistence layer used by the deployment; typical hosted configurations are designed to prevent such access.

First reported by: pucagit (CyStack).

## References
- https://github.com/langchain-ai/langgraph/security/advisories/GHSA-fjqc-hq36-qh5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-48775
- https://github.com/langchain-ai/langgraph
