# [H] PraisonAI recipe registry pull path traversal writes files outside the chosen output directory

## Summary
Severity: High
Advisory: GHSA-4rx4-4r3x-6534
CVE: CVE-2026-39306
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-4rx4-4r3x-6534
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.113

## Details
### Summary

PraisonAI's recipe registry pull flow extracts attacker-controlled `.praison` tar archives with `tar.extractall()` and does not validate archive member paths before extraction. A malicious publisher can upload a recipe bundle that contains `../` traversal entries and any user who later pulls that recipe will write files outside the output directory they selected.

This is a path traversal / arbitrary file write vulnerability on the client side of the recipe registry workflow. It affects both the local registry pull path and the HTTP registry pull path. The checksum verification does not prevent exploitation because the malicious traversal payload is part of the signed bundle itself.

### Details

The issue is caused by unsafe extraction of tar archive contents during recipe pull.

1. A malicious publisher creates a valid `.praison` bundle whose `manifest.json` is benign enough to pass publish, but whose tar members include traversal entries such as:

```text
../../escape-http.txt
```

2. `LocalRegistry.publish()` in `src/praisonai/praisonai/recipe/registry.py:214-287` only reads `manifest.json`, calculates a checksum, and stores the uploaded bundle. It does not inspect or sanitize the rest of the tar members before saving the archive.

3. When a victim later pulls the recipe from a local registry, `LocalRegistry.pull()` in `src/praisonai/praisonai/recipe/registry.py:289-345` extracts the tarball directly:

```python
recipe_dir = output_dir / name
recipe_dir.mkdir(parents=True, exist_ok=True)

with tarfile.open(bundle_path, "r:gz") as tar:
    tar.extractall(recipe_dir)
```

4. The HTTP client path is also vulnerable. `HttpRegistry.pull()` in `src/praisonai/praisonai/recipe/registry.py:691-739` downloads the bundle and then performs the same unsafe extraction:

```python
recipe_dir = output_dir / name
recipe_dir.mkdir(parents=True, exist_ok=True)

with tarfile.open(bundle_path, "r:gz") as tar:
    tar.extractall(recipe_dir)
```

5. Because no archive member validation is performed, traversal entries escape `recipe_dir` and create files elsewhere on disk.

Verified vulnerable behavior:

- Published recipe name: `evil-http`
- Victim-selected output directory: `/tmp/praisonai-pull-traversal-poc/victim-output`
- Artifact created outside that directory: `/tmp/praisonai-pull-traversal-poc/escape-http.txt`
- Artifact contents: `owned over http`

This demonstrates that a remote publisher can cause filesystem writes outside the pull destination chosen by another user.

### PoC

Run the single verification script from the checked-out repository:

```bash
cd "/Users/r1zzg0d/Documents/CVE hunting/targets/PraisonAI"
python3 tmp/pocs/poc2.py
```

Expected vulnerable output:

```text
[+] Publish result: {'ok': True, 'name': 'evil-http', 'version': '1.0.0', ...}
[+] Pull result: {'name': 'evil-http', 'version': '1.0.0', ...}
[+] Outside artifact exists: True
[+] Artifact also inside output dir: False
[+] Outside artifact content: 'owned over http\n'
[+] RESULT: VULNERABLE - pulling the recipe created a file outside the chosen output directory.
```

Then verify the created file manually:

```bash
ls -l /tmp/praisonai-pull-traversal-poc/escape-http.txt
cat /tmp/praisonai-pull-traversal-poc/escape-http.txt
find /tmp/praisonai-pull-traversal-poc -maxdepth 3 | sort
```

What the script does internally:

1. Starts a local PraisonAI recipe registry server.
2. Builds a malicious `.praison` bundle containing the tar entry `../../escape-http.txt`.
3. Publishes the malicious bundle to the local HTTP registry.
4. Simulates a victim pulling that recipe into `/tmp/praisonai-pull-traversal-poc/victim-output`.
5. Confirms that the file is created outside the chosen output directory.

### Impact

This is a path traversal / arbitrary file write vulnerability in the recipe pull workflow.

Impacted parties:

- Users who pull recipes from an untrusted or shared PraisonAI registry.
- Teams running internal registries where one publisher can influence what other users pull.
- Automated systems or CI jobs that fetch recipes into working directories near sensitive project files.

Security impact:

- Integrity impact is high because an attacker can create or overwrite files outside the expected extraction directory.
- Availability impact is significant if the overwritten target is a config file, project file, startup script, or another operational artifact.
- The issue crosses a real security boundary because the attacker only needs to publish a malicious recipe, while the victim triggers the write by pulling it.

### Remediation

1. Replace raw `tar.extractall()` with a safe extraction routine that validates every `TarInfo` member before extraction. Reject absolute paths, `..` segments, and any resolved path that escapes the intended extraction directory.

2. Apply the same archive member validation in both `LocalRegistry.pull()` and `HttpRegistry.pull()` so that local and remote registry clients share the same safety guarantees.

3. Consider validating tar contents during publish as well, so malicious bundles are rejected before they ever enter the registry and cannot be served to downstream users.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-4rx4-4r3x-6534
- https://nvd.nist.gov/vuln/detail/CVE-2026-39306
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.113
