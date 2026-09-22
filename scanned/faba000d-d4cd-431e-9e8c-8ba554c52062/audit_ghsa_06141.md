# [H] RabbitMQ Java client: Unvalidated Class.forName in JSON-RPC ProcedureDescription enables arbitrary class loading

## Summary
Severity: High
Advisory: GHSA-6g32-pxv4-2wfj
CVE: CVE-2026-63337
CWE: CWE-470
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-6g32-pxv4-2wfj
Type: github-advisory

## Affected
- Maven: `com.rabbitmq:amqp-client` — affected >=0 <5.33.0

## Details
The JSON-RPC tools in `com.rabbitmq.tools.jsonrpc` perform `Class.forName(javaReturnType)` with `initialize=true` on class names received from untrusted AMQP messages, without any validation or allowlist.

**Vulnerable code** (`ProcedureDescription.java:101-127`):
When a `JsonRpcClient` connects, it calls `system.describe` and receives a service description from the AMQP queue. The response JSON includes `javaReturnType` fields that are reflectively set via `JSONUtil.tryFill()`, triggering `setJavaReturnType()` → `computeReturnTypeAsJavaClass()` → `Class.forName(javaReturnType)`.

**Attack scenario:**
1. Victim uses `JsonRpcClient` to connect to a JSON-RPC service via RabbitMQ
2. Attacker (co-tenant on shared broker, or MITM) intercepts the `system.describe` request
3. Attacker responds with crafted `javaReturnType` values
4. Victim's client calls `Class.forName(attackerInput)` with default `initialize=true`
5. Static initializers of attacker-specified classes execute in victim's JVM

Additionally, the loaded class from `getReturnType()` is passed to `mapper.parse(replyStr, expectedType)` at `JsonRpcClient.java:168`, potentially enabling type-confusion.

**Recommended fix:** Use `Class.forName(javaReturnType, false, classLoader)` to prevent static initializer execution, or add an allowlist of permitted return types.

**CWE:** CWE-470

---

**Reply from reporter (2026-06-29):** Thanks for the quick turnaround. Fix looks good. Looking forward to the CVE assignment.

## References
- https://github.com/rabbitmq/rabbitmq-java-client/security/advisories/GHSA-6g32-pxv4-2wfj
- https://github.com/rabbitmq/rabbitmq-java-client/pull/2000
- https://github.com/rabbitmq/rabbitmq-java-client/pull/2002
- https://github.com/rabbitmq/rabbitmq-java-client/commit/0032f75f9dc3df847f94b2b85a16119250bf63cb
- https://github.com/rabbitmq/rabbitmq-java-client/commit/9f8e7efd0c648f235dc0e96232ae7efa75ea4fa8
- https://github.com/rabbitmq/rabbitmq-java-client
- https://github.com/rabbitmq/rabbitmq-java-client/releases/tag/v5.33.0
