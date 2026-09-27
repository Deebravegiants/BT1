# [H] datamodel-code-generator vulnerable to arbitrary local file read via JSON-Schema `$ref` (`file://` and `../` traversal), bypassing `--no-allow-remote-refs`

## Summary
Severity: High
Advisory: GHSA-8359-h9fx-j6v9
CVE: CVE-2026-55389
CWE: CWE-200, CWE-22, CWE-610
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-8359-h9fx-j6v9
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0 <0.62.0

## Details
### Summary

`datamodel-code-generator` resolves JSON-Schema `$ref` targets that point at the local filesystem without restricting them to the input/base directory and without honoring the remote-reference security control. In the default configuration, an attacker who controls an input schema (a "paste your OpenAPI/JSON-Schema" service, a CI job that generates models from a submitted spec, or any multi-tenant codegen platform) can read any file the process user can read and map the host filesystem. This works via either a `file://` absolute URI or a `../`-escaped relative reference, and it succeeds even when `--no-allow-remote-refs` is set.

This is an unauthenticated path-traversal / information-disclosure issue (CWE-22 / CWE-200) plus a bypass of a documented security control.

### Details

`is_url()` classifies `file://` as a URL (`reference.py:1249`):

```python
def is_url(ref: str) -> bool:
    return ref.startswith(("https://", "http://", "file://"))
```

The remote-ref gate then explicitly exempts `file://`, so `--no-allow-remote-refs` never applies to it (`parser/jsonschema.py`, `_get_ref_body`):

```python
if is_url(resolved_ref):
    if not resolved_ref.startswith("file://") and self.http_local_ref_path is None:
        if self.allow_remote_refs is False:
            raise Error(...)        # <-- skipped for file://
        ...
    return self._get_ref_body_from_url(resolved_ref)
return self._get_ref_body_from_remote(resolved_ref)
```

Both local-file branches read the target with **no containment check**. The `file://` branch reads any absolute path:

```python
# _get_ref_body_from_url
if ref.startswith("file://"):
    path = url2pathname(urlparse(ref).path)     # absolute path, anywhere on disk
    return self.remote_object_cache.get_or_put(
        ref, default_factory=lambda _: load_data_from_path(Path(path), self.encoding))
```

and the plain relative branch lets `../` escape the base directory:

```python
# _get_ref_body_from_remote
full_path = self.base_path / resolved_ref       # no is_relative_to(base_path) check
return self.remote_object_cache.get_or_put(
    str(full_path), default_factory=lambda _: load_data_from_path(full_path, self.encoding))
```

For contrast, the HTTP-local-ref branch (`_get_ref_body_from_local_http_path`) *does* enforce `is_relative_to(base_path)`; these two filesystem branches do not. (This is distinct from the previously reported HTTP `$ref`/`--url` SSRF hardened in `http.py`  these code paths never enter `http.py`.)

The fetched file is read and parsed, yielding two impacts:

1. **Arbitrary file read + filesystem oracle (any file).** The process opens any readable path, and the three distinguishable outcomes leak filesystem structure: `Expected dict, got str/list` = the file exists and was read into the process; `FileNotFoundError: '<abs path>'` = missing; `PermissionError: '<abs path>'` = exists but unreadable. An attacker uses this to probe arbitrary paths and recover the operator's absolute filesystem layout.

2. **Verbatim secret disclosure into the generated code.** When the referenced node is JSON-Schema-shaped, values in `const`/`default`/`enum`/`description` positions are emitted verbatim into the generated Python that is returned to the attacker — i.e. exactly the internal/private schema and config files a codegen host stores (specs with example/default tokens, default credentials, internal hostnames, service-account JSON, k8s secret manifests).

Scope note (to avoid overstating): the *raw bytes* of unstructured files such as `/etc/passwd` or a PEM `id_rsa` are read into the process but are not echoed verbatim into the output, because they parse to a single scalar and are rejected as "not a schema". For those files the impact is the read itself plus the existence/permission/absolute-path oracle; verbatim content disclosure applies to schema-shaped nodes.

### PoC

Self-contained reproducer: https://gist.github.com/thegr1ffyn/2a87e81f985883acc30d0118c52da4d3 /  (`poc.py` creates everything in a temp dir, runs the generator, asserts read + leak + gate bypass, and cleans up). 
Minimal manual reproduction of the arbitrary read (any path works):

```bash
printf '{"type":"object","properties":{"x":{"$ref":"file:///etc/passwd"}}}' > probe.json
datamodel-codegen --input probe.json --input-file-type jsonschema --output o.py
# -> "TypeError: Expected dict, got str"  == /etc/passwd was opened and fully parsed.
# Swap the $ref for a missing/unreadable path to see the existence/permission oracle.
```

### Impact

Arbitrary local file read / path traversal (CWE-22) → information disclosure (CWE-200), plus bypass of `--no-allow-remote-refs`. Any application, CI pipeline, or multi-tenant service that runs `datamodel-code-generator` on an untrusted schema and exposes (returns, logs, commits, renders) the generated code is affected. The attacker can: open and read any file the process user can read (demonstrated: `/etc/passwd`, a PEM `id_rsa`, paths under `/root/`); map the host filesystem and recover absolute paths; and exfiltrate secret values verbatim from any schema-shaped node. Attacker controls only the input schema; no authentication or special privileges required.

### Suggested remediation

1. Do not exempt `file://` from the `allow_remote_refs` gate, treat it as an external scheme.
2. In both `_get_ref_body_from_url` (the `file://` case) and `_get_ref_body_from_remote`, reject targets that are not `resolved.is_relative_to(self.base_path)`, mirroring the existing check in `_get_ref_body_from_local_http_path`.

### Maintainer status

Confirmed by maintainer review and regression tests. The private fix PR was merged and released in `0.62.0`: https://github.com/koxudaxi/datamodel-code-generator-ghsa-8359-h9fx-j6v9/pull/1

Fix summary: apply the remote-ref gate to `file://` refs and local JSON Schema refs outside the input base path. In `0.62.0`, `--no-allow-remote-refs` blocks these references; the default compatibility mode emits a `FutureWarning` and users who intentionally rely on trusted external local refs can pass `--allow-remote-refs`.

Release status: fixed in `0.62.0` for the documented `--no-allow-remote-refs` bypass, with a compatibility warning for the default behavior.

Validation: `uv run --group test --extra http pytest tests/main/jsonschema/test_main_jsonschema.py` passed locally; `uv run --group fix ruff check src/datamodel_code_generator/parser/jsonschema.py tests/main/jsonschema/test_main_jsonschema.py` passed.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-8359-h9fx-j6v9
- https://github.com/koxudaxi/datamodel-code-generator/commit/2ff4a72b4550a2b2069754c5b075b1655067e5fb
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.62.0
