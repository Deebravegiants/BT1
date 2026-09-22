# [C] Langflow has Authenticated Code Execution in Agentic Assistant Validation

## Summary
Severity: Critical
Advisory: GHSA-v8hw-mh8c-jxfc
CVE: CVE-2026-33873
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-v8hw-mh8c-jxfc
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.0

## Details
## Description

### 1. Summary

The Agentic Assistant feature in Langflow executes LLM-generated Python code during its **validation** phase. Although this phase appears intended to validate generated component code, the implementation reaches dynamic execution sinks and instantiates the generated class server-side.

In deployments where an attacker can access the Agentic Assistant feature and influence the model output, this can result in arbitrary server-side Python execution.

### 2. Description

#### 2.1 Intended Functionality

The Agentic Assistant endpoints are designed to help users generate and validate components for a flow. Users can submit requests to the assistant, which returns candidate component code for further processing.

A reasonable security expectation is that validation should treat model output as **untrusted text** and perform only static or side-effect-free checks.

The externally reachable endpoints are:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/api/router.py#L252-L297](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/api/router.py#L252-L297)

The request model accepts attacker-influenceable fields such as `input_value`, `flow_id`, `provider`, `model_name`, `session_id`, and `max_retries`:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/api/schemas.py#L20-L31](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/api/schemas.py#L20-L31)

#### 2.2 Root Cause

In the affected code path, Langflow processes model output through the following chain:

`/assist`
→ `execute_flow_with_validation()`
→ `execute_flow_file()`
→ LLM returns component code
→ `extract_component_code()`
→ `validate_component_code()`
→ `create_class()`
→ generated class is instantiated

The assistant service reaches the validation path here:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L58-L79](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L58-L79)

The code extraction step occurs here:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/helpers/code_extraction.py#L11-L53](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/helpers/code_extraction.py#L11-L53)

The validation entry point is here:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/helpers/validation.py#L27-L47](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/helpers/validation.py#L27-L47)

The issue is that this validation path is not purely static. It ultimately invokes `create_class()` in `lfx.custom.validate`, where Python code is dynamically executed via `exec(...)`, including both global-scope preparation and class construction.

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L241-L272](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L241-L272)

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L394-L399](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L394-L399)

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L441-L443](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L441-L443)

As a result, LLM-generated code is treated as executable Python rather than inert data. This means the “validation” step crosses a trust boundary and becomes an execution sink.

The streaming path can also reach this sink when the request is classified into the component-generation branch:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L142-L156](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L142-L156)

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L259-L300](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L259-L300)

### 3. Proof of Concept (PoC)

1. Send a request to the Agentic Assistant endpoint.
2. Provide input that causes the model to return malicious component code.
3. The returned code reaches the validation path.
4. During validation, the server dynamically executes the generated Python.
5. Arbitrary server-side code execution occurs.

### 4. Impact

* Attackers who can access the Agentic Assistant feature and influence model output may execute arbitrary Python code on the server.
* This can lead to:

  * OS command execution
  * file read/write
  * credential or secret disclosure
  * full compromise of the Langflow process

### 5. Exploitability Notes

This issue is most accurately described as an **authenticated or feature-reachable code execution vulnerability**, rather than an unconditional unauthenticated remote attack.

Severity depends on deployment model:

* In **local-only, single-user development setups**, the issue may be limited to self-exposure by the operator.
* In **shared, team, or internet-exposed deployments**, it may be exploitable by other users or attackers who can reach the assistant feature.

The assistant feature depends on an active user context:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/api/utils/core.py#L38](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/api/utils/core.py#L38)

Authentication sources include bearer token, cookie, or API key:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/services/auth/utils.py#L39-L53](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/services/auth/utils.py#L39-L53)

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/services/auth/utils.py#L156-L163](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/services/auth/utils.py#L156-L163)

Default deployment settings may widen exposure, including `AUTO_LOGIN=true` and the `/api/v1/auto_login` endpoint:

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/services/settings/auth.py#L71-L87](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/services/settings/auth.py#L71-L87)

[https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/api/v1/login.py#L96-L135](https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/api/v1/login.py#L96-L135)

### 6. Patch Recommendation

* Remove all dynamic execution from the validation path.
* Ensure validation is strictly static and side-effect-free.
* Treat all LLM output as untrusted input.
* If code generation must be supported, require explicit approval and run it in a hardened sandbox isolated from the main server process.

Discovered by: @kexinoh ([https://github.com/kexinoh](https://github.com/kexinoh), works at Tencent Zhuque Lab)

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-v8hw-mh8c-jxfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33873
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-82.yaml
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/services/settings/auth.py#L71-L87
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L441-L443
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L394-L399
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/lfx/src/lfx/custom/validate.py#L241-L272
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/services/auth/utils.py#L39-L53
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/services/auth/utils.py#L156-L163
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/api/v1/login.py#L96-L135
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/api/utils/core.py#L38
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L58-L79
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L259-L300
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/services/assistant_service.py#L142-L156
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/helpers/validation.py#L27-L47
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/helpers/code_extraction.py#L11-L53
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/api/schemas.py#L20-L31
- https://github.com/langflow-ai/langflow/blob/f7f4d1e70ba5eecd18162ec96f3571c2cfbcd1fc/src/backend/base/langflow/agentic/api/router.py#L252-L297
- https://github.com/langflow-ai/langflow
