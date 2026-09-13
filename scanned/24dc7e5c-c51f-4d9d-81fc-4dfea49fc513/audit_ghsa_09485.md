# [M] `potato-annotation` has a Project-Boundary Bypass

## Summary
Severity: Medium
Advisory: GHSA-q9m2-fhv9-3jcf
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-q9m2-fhv9-3jcf
Type: github-advisory

## Affected
- PyPI: `potato-annotation` — affected >=2.0.0 <2.4.5

## Details
## Summary
`validate_path_security` uses string-prefix containment (`startswith`) for boundary checks. This allows paths that are **outside** the intended project directory but share its prefix string (e.g., `/tmp/potato_proj_demo_evil/...` vs `/tmp/potato_proj_demo`) to be accepted.

## Details
### Affected source location (root cause)
**File:** `potato/server_utils/config_module.py`

**Snippet (lines 370–373):**
```python
real_path = os.path.realpath(normalized_path)
real_base = os.path.realpath(base_dir)
if not real_path.startswith(real_base):
    raise ConfigSecurityError(...)
```

**Snippet (lines 384–389):**
```python
real_path = os.path.realpath(normalized_path)
check_dir = project_dir if project_dir else base_dir
real_check_dir = os.path.realpath(check_dir)
if not real_path.startswith(real_check_dir):
    raise ConfigSecurityError(...)
```

`startswith()` is string-based, so `/tmp/potato_proj_demo_evil/...` passes when checked against `/tmp/potato_proj_demo`.

### Confirmed affected call sites
**File:** `potato/server_utils/config_module.py`

1) `validate_file_paths` task_dir branch (line 2113)
```python
validated_task_dir = validate_path_security(task_dir, project_dir)
```

2) `validate_file_paths` data_files branch (line 2151)
```python
validated_path = validate_path_security(file_path, base_dir, project_dir)
```

3) `validate_training_config` training.data_file branch (line 2286)
```python
validated_path = validate_path_security(data_file, base_dir, project_dir)
```

## PoC
```python
from potato.server_utils.config_module import validate_path_security

base = '/tmp/potato_proj_demo'
vuln = '/tmp/potato_proj_demo_evil/file.txt'

try:
    print('inside=', validate_path_security('/tmp/potato_proj_demo/file.txt', base, base))
except Exception as e:
    print('inside_error=', type(e).__name__, e)

try:
    validate_path_security('/tmp/other_demo/file.txt', base, base)
except Exception as e:
    print('baseline=', type(e).__name__, e)

print('trigger=', validate_path_security(vuln, base, base))
```

## Impact
- Can allow unauthorized sibling-prefix file access outside intended project boundary.
- Can affect read paths (`data_files`, `training.data_file`, `base_css`, `header_logo`) and output/path placement depending on configuration.

## References
- https://github.com/davidjurgens/potato/security/advisories/GHSA-q9m2-fhv9-3jcf
- https://github.com/davidjurgens/potato
