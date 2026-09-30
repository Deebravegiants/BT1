# [H] BentoML has Dockerfile Command Injection via system_packages in bentofile.yaml

## Summary
Severity: High
Advisory: GHSA-jfjg-vc52-wqvf
CVE: CVE-2026-33744
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-jfjg-vc52-wqvf
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.4.37

## Details
## Summary

The `docker.system_packages` field in `bentofile.yaml` accepts arbitrary strings that are interpolated directly into Dockerfile `RUN` commands without sanitization. Since `system_packages` is semantically a list of OS package names (data), users do not expect values to be interpreted as shell commands. A malicious `bentofile.yaml` achieves arbitrary command execution during `bentoml containerize` / `docker build`.

## Affected Component

- `src/_bentoml_sdk/images.py:85-89` — `.format(packages=" ".join(packages))` into shell command
- `src/bentoml/_internal/container/frontend/dockerfile/templates/base_debian.j2:13` — `{{ __options__system_packages | join(' ') }}`
- `src/bentoml/_internal/bento/build_config.py:174` — No validation on `system_packages`
- All distro install commands in `src/bentoml/_internal/container/frontend/dockerfile/__init__.py`

## Affected Versions

All versions supporting `docker.system_packages` in `bentofile.yaml`, confirmed on 1.4.36.

## Steps to Reproduce

1. Create a project directory with:

**service.py:**
```python
import bentoml

@bentoml.service
class MyService:
    @bentoml.api
    def predict(self) -> str:
        return "hello"
```

**bentofile.yaml:**
```yaml
service: "service:MyService"
docker:
  system_packages:
    - "curl && id > /tmp/bentoml-pwned #"
```

2. Run:
```bash
bentoml build
```

3. Examine the generated Dockerfile at `~/bentoml/bentos/my_service/<tag>/env/docker/Dockerfile`. Line 41 will contain:
```dockerfile
RUN apt-get install -q -y -o Dpkg::Options::=--force-confdef curl && id > /tmp/bentoml-pwned #
```

4. Running `bentoml containerize my_service:<tag>` will execute `id > /tmp/bentoml-pwned` as root during the Docker build.

## Root Cause

The `system_packages` field values are treated as package names (data) by the user but are string-formatted directly into shell commands in the Dockerfile:

```python
# images.py:85-89
self.commands.append(
    CONTAINER_METADATA[self.distro]["install_command"].format(
        packages=" ".join(packages)  # No escaping
    )
)
```

Where `install_command` is `"apt-get install -q -y -o Dpkg::Options::=--force-confdef {packages}"`.

A `bash_quote` filter (wrapping `shlex.quote`) exists in the codebase and is registered in both Jinja2 environments, but it is only applied to environment variable values, never to `system_packages`.

## Impact

1. **Malicious repositories**: An attacker publishes an ML project with a crafted `bentofile.yaml`. Anyone who clones and builds it gets arbitrary code execution during `docker build`.
2. **CI/CD compromise**: Automated pipelines running `bentoml containerize` on PRs that modify `bentofile.yaml` are vulnerable.
3. **BentoCloud**: If BentoCloud builds images from user-supplied `bentofile.yaml`, this could achieve RCE on cloud infrastructure.
4. **Supply chain**: Shared bentos or model repos in the BentoML ecosystem can contain malicious configs.

## Suggested Fix

### Option 1: Input validation (recommended)

Add a regex validator to `system_packages` in `build_config.py`:

```python
import re

VALID_PACKAGE_NAME = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9.+\-_:]*$')

def _validate_system_packages(instance, attribute, value):
    if value is None:
        return
    for pkg in value:
        if not VALID_PACKAGE_NAME.match(pkg):
            raise BentoMLException(
                f"Invalid system package name: {pkg!r}. "
                "Package names may only contain alphanumeric characters, "
                "dots, plus signs, hyphens, underscores, and colons."
            )

system_packages: t.Optional[t.List[str]] = attr.field(
    default=None, validator=_validate_system_packages
)
```

### Option 2: Output escaping

Apply `shlex.quote()` to each package name before interpolation in `images.py:system_packages()` and apply the `bash_quote` Jinja2 filter in `base_debian.j2`.

## References
- https://github.com/bentoml/BentoML/security/advisories/GHSA-jfjg-vc52-wqvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33744
- https://github.com/bentoml/BentoML
- https://github.com/pypa/advisory-database/tree/main/vulns/bentoml/PYSEC-2026-157.yaml
