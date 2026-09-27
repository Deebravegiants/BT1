# [H] MLFLOW_ALLOW_PICKLE_DESERIALIZATION=False safety control bypassed by mlflow.statsmodels flavor — RCE via crafted model artifact

## Summary
Severity: High
Advisory: GHSA-gqvg-gmmx-x4hm
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-gqvg-gmmx-x4hm
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=2.1.0 <3.15.0

## Details
## Summary

MLflow introduced `MLFLOW_ALLOW_PICKLE_DESERIALIZATION` as a security control to prevent unsafe `pickle.load` execution during model loading, in response to CVE-2024-37052 through CVE-2024-37060. When set to `False`, operators expect all pickle deserialization to be blocked. The most recent related fix (#21188) patched a bypass in the pyfunc flavor.

However, the `mlflow.statsmodels` flavor completely omits this guard. An attacker who places a crafted MLmodel artifact into any accessible artifact store can trigger arbitrary code execution on any process that calls `mlflow.pyfunc.load_model()` against the malicious model — **even when `MLFLOW_ALLOW_PICKLE_DESERIALIZATION=False`**.

This is a security control bypass. The operator believes pickle RCE is mitigated; the statsmodels flavor silently ignores the control.

---

## Root Cause

`mlflow.pyfunc.load_model()` dispatches to flavor `_load_pyfunc` implementations via:

```
# mlflow/pyfunc/__init__.py L1170-1172
model_impl = importlib.import_module(conf[MAIN])._load_pyfunc(data_path)
```

The guarded pattern (from `mlflow/sklearn/__init__.py` L526-533, the reference implementation) is:

```
if (
    not MLFLOW_ALLOW_PICKLE_DESERIALIZATION.get()
    and not is_in_databricks_runtime()
    and not is_in_databricks_model_serving_environment()
):
    raise MlflowException("Deserializing model using pickle is disallowed...")
```

`mlflow/statsmodels/__init__.py` has **no such check**:

```
# L307-320 — no guard anywhere in this file
def _load_model(path):
    import statsmodels.iolib.api as smio
    return smio.load_pickle(path)   # calls pickle.load() directly

def _load_pyfunc(path):
    return _StatsmodelsModelWrapper(_load_model(path))
```

`statsmodels.iolib.api.load_pickle` is a thin wrapper around `pickle.load`. Its own docstring warns: *"Never unpickle data received from an untrusted or unauthenticated source."*

---

## Trigger

An attacker crafts an MLmodel YAML that specifies `mlflow.statsmodels` as the loader module:

```
flavors:
  python_function:
    loader_module: mlflow.statsmodels
    data: model.pkl
  statsmodels:
    data: model.pkl
    statsmodels_version: 0.14.0
```

With a malicious `model.pkl` placed alongside it in the artifact store, any call to:

```
os.environ["MLFLOW_ALLOW_PICKLE_DESERIALIZATION"] = "False"
mlflow.pyfunc.load_model("models:/MaliciousModel/1")
```

...deserializes the pickle file with **no guard check**, executing arbitrary code with the privileges of the calling process.

On default MLflow deployments (no `--app-name basic-auth`), authentication is disabled, so artifact upload requires no credentials.

---

## Affected Code

- `mlflow/statsmodels/__init__.py` L307-310: `_load_model` — calls `smio.load_pickle` without checking `MLFLOW_ALLOW_PICKLE_DESERIALIZATION`
- `mlflow/statsmodels/__init__.py` L313-320: `_load_pyfunc` — dispatches to `_load_model` without checking the control

Permalink (commit `0b0c576c`):
- https://github.com/mlflow/mlflow/blob/0b0c576c642b5b0d9496c829809c7d097403bc9f/mlflow/statsmodels/__init__.py#L307-L310
- https://github.com/mlflow/mlflow/blob/0b0c576c642b5b0d9496c829809c7d097403bc9f/mlflow/statsmodels/__init__.py#L313-L320

---

## Recommended Fix

Add the missing guard to `mlflow/statsmodels/__init__.py`:

```
from mlflow.environment_variables import MLFLOW_ALLOW_PICKLE_DESERIALIZATION
from mlflow.utils.databricks_utils import (
    is_in_databricks_model_serving_environment,
    is_in_databricks_runtime,
)

def _load_model(path):
    if (
        not MLFLOW_ALLOW_PICKLE_DESERIALIZATION.get()
        and not is_in_databricks_runtime()
        and not is_in_databricks_model_serving_environment()
    ):
        raise MlflowException(
            "Deserializing model using pickle is disallowed, but this statsmodels "
            "model requires pickle deserialization. Set environment variable "
            "'MLFLOW_ALLOW_PICKLE_DESERIALIZATION' to 'true' to allow this."
        )
    import statsmodels.iolib.api as smio
    return smio.load_pickle(path)
```

## References
- https://github.com/mlflow/mlflow/security/advisories/GHSA-gqvg-gmmx-x4hm
- https://github.com/mlflow/mlflow/pull/24686
- https://github.com/mlflow/mlflow/commit/38615289094a4b700a20b5d1dbfbe57bdfb0411f
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/releases/tag/v3.15.0
