# [H] PraisonAI recipe registry publish path traversal allows out-of-root file write

## Summary
Severity: High
Advisory: GHSA-r9x3-wx45-2v7f
CVE: CVE-2026-39308
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-r9x3-wx45-2v7f
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.113

## Details
### Summary

PraisonAI's recipe registry publish endpoint writes uploaded recipe bundles to a filesystem path derived from the bundle's internal `manifest.json` before it verifies that the manifest `name` and `version` match the HTTP route. A malicious publisher can place `../` traversal sequences in the bundle manifest and cause the registry server to create files outside the configured registry root even though the request is ultimately rejected with HTTP `400`.

This is an arbitrary file write / path traversal issue on the registry host. It affects deployments that expose the recipe registry publish flow. If the registry is intentionally run without a token, any network client that can reach the service can trigger it. If a token is configured, any user with publish access can still exploit it.

### Details

The bug is caused by the order of operations between the HTTP handler and the registry storage layer.

1. `RegistryServer._handle_publish()` in `src/praisonai/praisonai/recipe/server.py:370-426` parses `POST /v1/recipes/{name}/{version}`, writes the uploaded `.praison` file to a temporary path, and immediately calls:

```python
result = self.registry.publish(tmp_path, force=force)
```

2. `LocalRegistry.publish()` in `src/praisonai/praisonai/recipe/registry.py:214-287` opens the uploaded tarball, reads `manifest.json`, and trusts the attacker-controlled `name` and `version` fields:

```python
name = manifest.get("name")
version = manifest.get("version")
recipe_dir = self.recipes_path / name / version
recipe_dir.mkdir(parents=True, exist_ok=True)
bundle_name = f"{name}-{version}.praison"
dest_path = recipe_dir / bundle_name
shutil.copy2(bundle_path, dest_path)
```

3. Validation helpers already exist in the same file:

```python
def _validate_name(name: str) -> bool:
def _validate_version(version: str) -> bool:
```

but they are not called before the filesystem write.

4. Only after `publish()` returns does the route compare the manifest values with the URL values:

```python
if result["name"] != name or result["version"] != version:
    self.registry.delete(result["name"], result["version"])
    return self._error_response(...)
```

At that point the out-of-root artifact has already been created. The request returns an error, but the write outside the registry root remains on disk.

Verified vulnerable behavior:

- Request path: `/v1/recipes/safe/1.0.0`
- Internal manifest name: `../../outside-dir`
- Server response: HTTP `400`
- Leftover artifact: `/tmp/praisonai-publish-traversal-poc/outside-dir-1.0.0.praison`

This demonstrates that the write occurs before the consistency check and rollback.

### PoC

Run the single verification script from the checked-out repository:

```bash
cd "/Users/r1zzg0d/Documents/CVE hunting/targets/PraisonAI"
python3 tmp/pocs/poc.py
```

Expected vulnerable output:

```text
[+] Publish response status: 400
{
  "ok": false,
  "error": "Bundle name/version (../../outside-dir@1.0.0) doesn't match URL (safe@1.0.0)",
  "code": "error"
}
[+] Leftover artifact exists: True
[+] Artifact under registry root: False
[+] RESULT: VULNERABLE - upload was rejected, but an out-of-root artifact was still created.
```

Then verify the artifact manually:

```bash
ls -l /tmp/praisonai-publish-traversal-poc/outside-dir-1.0.0.praison
find /tmp/praisonai-publish-traversal-poc -maxdepth 2 | sort
```

What the script does internally:

1. Starts a local PraisonAI recipe registry server.
2. Builds a malicious `.praison` bundle whose internal `manifest.json` contains `name = ../../outside-dir`.
3. Uploads that bundle to the apparently safe route `/v1/recipes/safe/1.0.0`.
4. Receives the expected `400` mismatch error.
5. Confirms that `outside-dir-1.0.0.praison` was still written outside the configured registry directory.

### Impact

This is a path traversal / arbitrary file write vulnerability in the recipe registry publish flow.

Impacted parties:

- Registry operators running the PraisonAI recipe registry service.
- Any deployment that allows remote recipe publication.
- Any environment where adjacent writable filesystem locations contain sensitive application data, service files, or staged content that could be overwritten or planted.

Security impact:

- Integrity impact is high because an attacker can create or overwrite files outside the registry root.
- Availability impact is possible if the attacker targets adjacent runtime or application files.
- The issue can be chained with other local loading or deployment behaviors if nearby files are later consumed by another component.

### Remediation

1. Validate `manifest.json` `name` and `version` before any path join or filesystem write. Reject path separators, `..`, absolute paths, and any value that fails the existing `_validate_name()` / `_validate_version()` checks.

2. Resolve the final destination path and enforce that it remains under the configured registry root before calling `mkdir()` or `copy2()`. For example, compare the resolved destination against `self.recipes_path.resolve()`.

3. Move the URL-to-manifest consistency check ahead of `self.registry.publish(...)`, or refactor `publish()` so it receives already-validated route parameters instead of trusting attacker-controlled manifest values for storage paths.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-r9x3-wx45-2v7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-39308
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.113
