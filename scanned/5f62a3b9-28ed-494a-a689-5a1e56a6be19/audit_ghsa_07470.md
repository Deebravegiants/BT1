# [M] Open WebUI: Arena task endpoints can bypass underlying model access controls

## Summary
Severity: Medium
Advisory: GHSA-m3qf-58wf-w979
CVE: CVE-2026-59225
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-m3qf-58wf-w979
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.8.12 <0.10.0

## Details
## Summary

An authenticated non-admin user with read access to an arena wrapper model can reach a restricted underlying model through task endpoints such as `/api/v1/tasks/moa/completions`.

The normal chat route resolves arena models before the final chat dispatch and therefore re-checks the selected underlying model. The task routes call `utils.chat.generate_chat_completion()` directly. In that direct path, arena fallback resolution happens after the wrapper access check and then recurses with `bypass_filter=True`, skipping the selected submodel's access check.

## Technical Details

Open WebUI's current model-access behavior already denies direct access to the restricted model. The normal chat path also denies the selected restricted model after arena preprocessing. The task endpoint path is inconsistent with that protected behavior because it reaches the same restricted model only through the direct arena fallback and recursive `bypass_filter=True`.

This report does not rely on malicious provider configuration, user-authored Tools/Functions, or direct code execution. The crossed boundary is model read authorization.

Although the arena wrapper must be readable by the user, this is not just an "admin exposed a restricted model" configuration claim. The same configured arena is denied by the normal chat post-preprocessor control once the selected restricted model is the dispatch target. The bypass is specific to task endpoints that skip that preprocessor and enter the fallback arena resolver.

Official documentation also points to this interpretation:

- Open WebUI documents model access control as restricting models to specific users or groups.
- The workspace-model documentation treats "wrapper checked, restricted underlying model reached" as broken access control and recommends independent entries for curated deployments.
- The evaluation documentation describes arena mode as an evaluation/comparison feature that randomly selects models to compare, not as a feature that grants access to otherwise restricted models.
- This is not an unsafe-admin-action report: the same intended model access restriction is enforced on the direct model path and on the normal-chat selected-model control, then bypassed only through the task endpoint call order.

## PoV

The attached local PoV does not start a server and does not contact any model provider. It imports the current Open WebUI task endpoint and replaces provider dispatch plus model-access checks with local stubs so the call graph can be observed safely.

Observed result:

| Case | Expected | Actual |
| --- | --- | --- |
| Direct task request with `model=restricted-model` | Denied before provider dispatch | Denied; no provider call recorded |
| Normal-chat post-preprocessor control with `model=restricted-model` and `metadata.selected_model_id=restricted-model` | Denied before provider dispatch | Denied; no provider call recorded |
| Task request with `model=public-arena` that selects `restricted-model` | Denied when selected model is restricted | Local provider stub reached with `model=restricted-model` and `bypass_filter=true` |

In the arena task case, the restricted model is absent from the access-check log.

## Impact

A regular user can use a readable arena wrapper as an oracle for a restricted model via task-generation endpoints. For `/api/v1/tasks/moa/completions`, the caller controls the task prompt and receives the generated response.

The crossed security boundary is model read authorization: a non-admin user who is denied direct access to a model can still cause Open WebUI to dispatch a request to that model with the operator-configured backend credentials.

This can allow:

- use of paid or internal models with the admin-configured provider key;
- bypass of model access grants shown in the model selector;
- cost and usage impact on pay-per-token providers;
- exposure of model behavior or internal deployment capabilities that admins intended to restrict.

Suggested CVSS v3.1: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L` = 7.6.

Primary CWE: CWE-862, Missing Authorization.

Authentication is required, so `PR:L` is used. User interaction is not required. The confidentiality impact is High because the attacker can query a model the administrator intended to restrict. Integrity and availability are Low because the request can consume provider quota and produce model output under an authorization decision the system would otherwise deny.

This should not be Critical: exploitation requires an authenticated user and a readable arena wrapper, does not cross into another security authority, and does not provide arbitrary code execution or full instance compromise.

## Suggested Fix

Do not use `bypass_filter=True` for arena fallback dispatch unless the selected underlying model has already been authorized for the caller.

Recommended changes:

- after selecting `selected_model_id`, load the selected model and call `check_model_access(user, selected_model)` before recursive dispatch;
- for `filter_mode=exclude` or empty `model_ids`, build the candidate pool from models the current user can read, not every non-arena model in `request.app.state.MODELS`;
- add regression tests for `/api/v1/tasks/moa/completions`, `/api/v1/tasks/title/completions`, `/api/v1/tasks/tags/completions`, and normal `/api/chat/completions` arena behavior.

## Appendix: Affected Components

- `backend/open_webui/routers/tasks.py`
- `/api/v1/tasks/moa/completions` builds a payload from caller-controlled `model`, `prompt`, and `responses`, then calls `generate_chat_completion(request, form_data=payload, user=user)`.
- `backend/open_webui/utils/chat.py`
- checks access for the user-supplied arena wrapper model.
- fallback arena resolution selects an underlying model when the caller did not pass through `process_chat_payload()`.
- recursive dispatch uses `bypass_filter=True`.
- `backend/open_webui/utils/models.py`
- arena wrapper access checks only wrapper `access_grants`.

Current-head references:

- `backend/open_webui/routers/tasks.py:662-707`
- `backend/open_webui/utils/chat.py:190-204`
- `backend/open_webui/utils/chat.py:215-240`
- `backend/open_webui/utils/chat.py:248-269`
- `backend/open_webui/utils/middleware.py:2323-2347`
- `backend/open_webui/utils/models.py:378-407`

## Appendix: Duplicate Analysis

This is distinct from `GHSA-9vvh-qmjx-p4q8` / `CVE-2026-44555`, which covers `base_model_id` chaining and user-created workspace models. Current head includes the base-model-chain access fix through `has_base_model_access`.

This report covers task endpoints that call `generate_chat_completion()` without the main chat preprocessor. The root cause is arena fallback plus recursive `bypass_filter=True`, not `base_model_id`.

Live duplicate sweep before submission also reviewed:

- `GHSA-v6qf-75pr-p96m`: exposed HTTP query parameter `?bypass_filter=true`. This report does not rely on caller-controlled query parameters; the task endpoint reaches the server-side recursive `bypass_filter=True` path after arena fallback resolution.
- `GHSA-hp5m-24vp-vq2q`: `/api/openai/responses` passthrough missing model authorization. This report targets `/api/v1/tasks/moa/completions` and the arena resolver inside `utils.chat.generate_chat_completion()`.
- `GHSA-gfm2-xm6c-37qc`: chat ownership authorization in completions. This report does not require another user's chat ID.

If maintainers prefer to treat this as the same broad "wrapper checked, underlying model not checked" class, it should still be a distinct exploitation vector and affected component: task endpoints, not model creation/import or `base_model_id` dispatch.

## Appendix: Preconditions

- Authenticated non-admin user.
- The user can read an arena wrapper model, for example a custom arena with a public read grant.
- The arena model includes at least one restricted underlying model that the user cannot query directly.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-m3qf-58wf-w979
- https://nvd.nist.gov/vuln/detail/CVE-2026-59225
- https://github.com/open-webui/open-webui/pull/26046
- https://github.com/open-webui/open-webui/commit/dc4924b66e655b315e3be4430a3e51b7d5c20acc
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
