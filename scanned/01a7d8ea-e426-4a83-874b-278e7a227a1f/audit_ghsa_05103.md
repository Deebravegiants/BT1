# [M] pydantic-settings: NestedSecretsSettingsSource follows symlinks outside secrets_dir, enabling local file read and bypassing secrets_dir_max_size

## Summary
Severity: Medium
Advisory: GHSA-4xgf-cpjx-pc3j
CWE: CWE-22, CWE-400, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-4xgf-cpjx-pc3j
Type: github-advisory

## Affected
- PyPI: `pydantic-settings` — affected >=2.12.0 <2.14.2

## Details
### Summary

`NestedSecretsSettingsSource` reads secret values from files in a configured `secrets_dir`. When `secrets_nested_subdir=True`, a directory entry inside `secrets_dir` that is a symbolic link pointing **outside** `secrets_dir` is followed, so files outside the configured directory are read into settings values. The same code path bypasses the documented `secrets_dir_max_size` protection. An attacker or lower-privileged component able to influence entries in the configured secrets directory (for example, a writable or shared secrets mount) can turn this into an unintended local file read into settings and can defeat the advertised loading-size cap. This report does not claim network reachability by itself.

### Details

`NestedSecretsSettingsSource` performed two passes over `secrets_dir` using two different, inconsistent directory-traversal implementations:

* The size check in `validate_secrets_path()` used `Path.glob('**/*')`, which does **not** descend into a symbolically-linked directory.
* The loader in `load_secrets()` used `glob.iglob(f'{path}/**/*', recursive=True)` followed by `read_text()`, which **does** follow symlinked directories and reads through the link target.

Because the two passes disagreed on symlinks, a symlinked directory inside `secrets_dir` whose target lives elsewhere was invisible to the size accounting (counted as 0 bytes) while still being fully read by the loader. This produces two distinct problems:

1. **Out-of-tree read (CWE-22 / CWE-59).** A symlinked directory (or file) inside `secrets_dir` that resolves outside it is followed, and the external file's contents are loaded into the corresponding settings field.
2. **`secrets_dir_max_size` bypass (CWE-400).** The size check never sees the out-of-tree content, so the documented size cap is neither respected nor able to reject the oversized external file. A related amplification exists for cyclic in-tree symlinks, which `glob.iglob(recursive=True)` re-traverses, inflating the size accounting and the number of loaded secrets.

#### Reproduction

In a clean Linux container, with a `secrets_dir` containing a symlink `secrets/db -> /path/outside` and an `outside/passwd` file of 512 bytes, while `secrets_dir_max_size=100`:

```python
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    NestedSecretsSettingsSource,
)


class Db(BaseModel):
    passwd: str | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir='secrets',
        secrets_nested_subdir=True,
        secrets_dir_max_size=100,  # outside/passwd is 512 bytes
    )
    db: Db = Db()

    @classmethod
    def settings_customise_sources(
        cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings
    ):
        return (NestedSecretsSettingsSource(file_secret_settings),)
```

On affected versions, `Settings().db.passwd` is populated with the 512-byte out-of-tree file and **no** `SettingsError` is raised, even though the file exceeds `secrets_dir_max_size`.

### Impact

Applications that opt into `NestedSecretsSettingsSource` with `secrets_nested_subdir=True` and load secrets from a directory whose entries can be influenced by an attacker or a lower-privileged component (for example, a writable or shared secrets mount, or a secrets directory partially populated from untrusted input) are affected. The impact is:

* **Confidentiality:** files outside the configured `secrets_dir` can be read into settings values (local file read).
* **Integrity / availability of the safeguard:** the advertised `secrets_dir_max_size` cap can be bypassed, and cyclic symlinks can inflate resource usage during loading.

The vulnerability requires the ability to place a symbolic link inside the configured secrets directory; it is not remotely reachable on its own. Applications that do not use `NestedSecretsSettingsSource`, or that point `secrets_dir` at a directory fully under the application's control, are not affected.

### Mitigation

Upgrade to **pydantic-settings 2.14.2**, which:

* walks the secrets directory explicitly and only descends into directories whose resolved path stays within `secrets_dir`, so symlinked directories pointing outside are never followed;
* uses a single, cycle-safe iterator for both the size check and the loader, so the size accounting and the loaded set are always consistent and each real directory is visited at most once;
* skips any file whose resolved path escapes `secrets_dir`, as defense in depth.

If upgrading is not immediately possible, ensure the configured `secrets_dir` is fully owned and controlled by the application (no writable or attacker-influenced entries), or avoid `secrets_nested_subdir=True`.

## References
- https://github.com/pydantic/pydantic-settings/security/advisories/GHSA-4xgf-cpjx-pc3j
- https://github.com/pydantic/pydantic-settings
