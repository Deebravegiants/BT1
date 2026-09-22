# [H] datamodel-code-generator vulnerable to SSRF via JSON-Schema `$ref` to HTTP URL (silent by default)

## Summary
Severity: High
Advisory: GHSA-954p-556p-r752
CVE: CVE-2026-54690
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-954p-556p-r752
Type: github-advisory

## Affected
- PyPI: `datamodel-code-generator` — affected >=0.9.1 <0.61.0

## Details
### Summary

JSON-Schema `$ref` values pointing at HTTP or HTTPS URLs are silently dereferenced by `datamodel-code-generator` with no IP/host validation, no scheme allow-list, and redirects followed unconditionally. The `--allow-remote-refs` gate added in 0.56.0 defaults to `None`, which only emits a deprecation warning and then fetches the URL anyway; only explicit `--allow-remote-refs=false` blocks the request. The fetched body is parsed as a sub-schema and reflected verbatim into the generated `.py` source. As a result, any JSON-Schema document the developer feeds to `datamodel-codegen` — including documents authored by an attacker — can pivot to arbitrary internal addresses and leak the response into the generated code, with no developer cooperation beyond running the tool.

### Details

Sink: `src/datamodel_code_generator/parser/jsonschema.py`, `_get_ref_body` (lines 4776–4793, at tag `0.60.1` / commit `a321547e`):

```python
def _get_ref_body(self, resolved_ref: str) -> dict[str, YamlValue]:
    if is_url(resolved_ref):
        if not resolved_ref.startswith("file://") and self.http_local_ref_path is None:
            if self.allow_remote_refs is False:
                raise Error(f"Fetching remote $ref is disabled: {resolved_ref}...")
            if self.allow_remote_refs is None:
                warn_deprecated(                            # (A) warn only
                    "behavior.remote-ref-default",
                    details=f"Reference: {resolved_ref}",
                    stacklevel=2,
                )
        return self._get_ref_body_from_url(resolved_ref)    # (B) fetch fires
    return self._get_ref_body_from_remote(resolved_ref)
```

- (A) emits a deprecation warning when `allow_remote_refs` is its default (`None`); execution falls through to (B).
- (B) routes the URL through `_get_text_from_url` → `get_body`, the same fetcher described in other report — no IP validation, redirects followed.

The fetched body is then parsed as a sub-schema and merged into the model graph, so `description`, `title`, `properties`, etc. from the remote document end up in the generated `.py` source.

Only affects users who installed the `[http]` extra (`pip install 'datamodel-code-generator[http]'`).

### PoC

A self-contained one-file PoC is available here: https://gist.github.com/thegr1ffyn/562a6972d7dc3f2869458ae93fc608c0

### Impact

**Who is impacted.** Anyone running `datamodel-codegen` on a JSON-Schema or OpenAPI document of uncertain provenance, with the `[http]` extra installed. Real-world scenarios:

1. **Trojaned OpenAPI document.** A public REST API publishes `openapi.yaml`. One `$ref` points at `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>`; running `datamodel-codegen` against the spec from an EC2 instance leaks the IAM credentials into the generated client.
2. **Customer-supplied JSON Schema.** A B2B SaaS auto-generates client code from customer-uploaded schemas. The customer adds an HTTP `$ref` to `http://internal-admin:8080/users.json`; the response (e.g. JSON user list) ends up in the generated Python the SaaS hands back to the customer.
3. **CI on a private network.** A PR adds `schemas/inbound.json` with an HTTP `$ref` pointed at a service reachable only from the CI cluster's VPC; the CI runner fetches it and the generated `.py` leaks the response in PR artifacts.

Higher real-world risk than the sibling CLI-flag SSRF (other SSRF in this report bundle) because the *schema author* chooses the destination — the developer doesn't have to type any URL.

**Suggested fix.**

1. Flip the default in `parser/base.py`: `allow_remote_refs: bool = False`, and remove the silent-fetch-with-warning fallback at `parser/jsonschema.py:4786-4791`.
2. When fetching is allowed, apply the same IP/host validation proposed for other submitted SSRF report to both the initial `$ref` URL and every redirect target.
3. Document HTTP `$ref` in a third-party schema as equivalent to running `curl` on the developer's host.

### Maintainer resolution

This `$ref` report is fixed by the same shared HTTP fetcher hardening that resolved GHSA-rfr2-mq9m-x2qx. The code landed through the GHSA-rfr2 private security PR koxudaxi/datamodel-code-generator-ghsa-rfr2-mq9m-x2qx#1 and was merged into the public repository as 5fdba4a09f2d7a9996a504975b7ef7d63e3715bb. Follow-up generated-file and coverage fixes were merged in koxudaxi/datamodel-code-generator#3279 and docs were synced in #3280. The patched release is 0.61.0.

No separate net code diff remains in the GHSA-954 private PR because the shared HTTP fetcher patch is already present on `main`. This advisory remains separate because the affected entry point is remote JSON Schema/OpenAPI `$ref` resolution rather than direct CLI `--url` input.

The fix does not flip the `--allow-remote-refs` compatibility default in this patch. Instead, it mitigates the SSRF issue by blocking localhost, loopback, private, link-local, reserved, and other non-public network targets by default, validating every redirect target before it is fetched, and requiring `--allow-private-network` / `allow_private_network=True` for trusted internal schema endpoints. Remote `$ref` fetching remains controlled by `--allow-remote-refs`; non-public/internal targets additionally require `--allow-private-network`.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/koxudaxi/datamodel-code-generator/security/advisories/GHSA-954p-556p-r752
- https://github.com/koxudaxi/datamodel-code-generator/commit/5fdba4a09f2d7a9996a504975b7ef7d63e3715bb
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/koxudaxi/datamodel-code-generator/releases/tag/0.61.0
