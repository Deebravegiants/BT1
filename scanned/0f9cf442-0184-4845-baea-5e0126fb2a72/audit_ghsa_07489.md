# [H] datamodel-code-generator vulnerable to SSRF via --url: no host/IP validation, follows redirects

## Summary
Severity: High
Advisory: GHSA-rfr2-mq9m-x2qx
CVE: CVE-2026-54691
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-rfr2-mq9m-x2qx
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0.9.1 <0.61.0

## Details
### Summary

`datamodel-code-generator`'s built-in HTTP fetcher (`http.get_body`) issues an `httpx.GET` against any URL passed to `--url` (or reached via a redirect chain) with **no allow-list, no deny-list, no IP/host validation, and `follow_redirects=True`**. Loopback addresses, RFC1918 ranges, link-local (`169.254.169.254` cloud metadata), unique-local IPv6 and any other network-accessible target are all reachable. The JSON/YAML response body is parsed as a schema and reflected into the generated `.py` source, exfiltrating the response to anyone with access to that file (commonly committed to a repository).

### Details

Sink: `src/datamodel_code_generator/http.py`, `get_body` (lines 31–61, at tag `0.60.1` / commit `a321547e`):

```python
def get_body(url, headers=None, ignore_tls=False,
             query_parameters=None, timeout=DEFAULT_HTTP_TIMEOUT) -> str:
    httpx = _get_httpx()
    try:
        response = httpx.get(
            url,
            headers=headers,
            verify=not ignore_tls,
            follow_redirects=True,          # (A)
            params=query_parameters,
            timeout=timeout,
        )
    except Exception as e:
        ...
    if response.status_code >= 400:
        ...
    content_type = response.headers.get("content-type", "").lower()
    if "text/html" in content_type:
        raise SchemaFetchError(...)         # (B) — only filter
    return response.text                    # (C) → embedded in generated.py
```

- (A) follows redirects unconditionally — a public URL → 302 → internal address chain works.
- (B) the only filter is rejecting `text/html`. Non-HTML internal endpoints (JSON APIs, cloud metadata, admin services) pass through.
- (C) the response body becomes the schema; its `title`, `description`, `properties`, etc. land in the generated `.py` as class attributes and `Field(description=...)` strings.

`get_body` is called by `parser/base.py:1326` (`_get_text_from_url`), which is reached from CLI argument `--url <URL>`. (The `$ref` path is a separate advisory — see GHSA-D.)

Only affects users who installed the `[http]` extra (`pip install 'datamodel-code-generator[http]'`).

### PoC

A self-contained one-file PoC available here:
https://gist.github.com/thegr1ffyn/18de777d6c800a3b47715425e3f3e8f5

### Impact

**Who is impacted.** Anyone who runs `datamodel-codegen` with a `--url` they didn't fully verify, or who runs it inside a network with reachable internal services. Realistic scenarios:

1. **Trojan documentation / README.** A blog post or README example reads `datamodel-codegen --url https://schemas.example.com/user.json -o user.py`. The attacker controls `example.com`, redirects to `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>`, and the IAM credentials end up as a docstring in `user.py`.
2. **Internal port scan / disclosure.** Iterating `--url http://127.0.0.1:<port>/health` probes localhost services; non-HTML, non-error responses confirm a service and leak its body into the generated file.
3. **CI poisoning.** A PR adds a Makefile rule that calls `datamodel-codegen --url $(SCHEMA_URL)`; the CI runner reaches every internal service in its VPC and the response lands in PR artifacts.

**Suggested fix.** Resolve the URL host, reject loopback / private / link-local / multicast / reserved IPs by default, disable redirects by default (`follow_redirects=False`), re-validate after each redirect if the user opts into following them, and add an `--allow-private-network` flag for opt-in legitimate use.

### Maintainer resolution

This report was fixed together with GHSA-954p-556p-r752 by the private security PR koxudaxi/datamodel-code-generator-ghsa-rfr2-mq9m-x2qx#1, merged into the public repository as 5fdba4a09f2d7a9996a504975b7ef7d63e3715bb. Follow-up generated-file and coverage fixes were merged in koxudaxi/datamodel-code-generator#3279 and docs were synced in #3280. The patched release is 0.61.0.

The patch hardens the shared HTTP fetcher used by both direct CLI `--url` fetching and remote JSON Schema/OpenAPI `$ref` resolution:

- validates HTTP(S) URLs before fetching;
- blocks localhost, loopback, private, link-local, reserved, and other non-public network targets by default;
- disables automatic redirect following and validates each redirect target before requesting it;
- adds `--allow-private-network` / `allow_private_network=True` as an explicit opt-in for trusted internal schema endpoints.

Remote `$ref` fetching remains controlled by `--allow-remote-refs`; non-public/internal targets additionally require `--allow-private-network`.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-rfr2-mq9m-x2qx
- https://github.com/koxudaxi/datamodel-code-generator/commit/5fdba4a09f2d7a9996a504975b7ef7d63e3715bb
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.61.0
