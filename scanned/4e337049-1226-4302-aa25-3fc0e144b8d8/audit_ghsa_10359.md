# [M] Copier `_external_data` allows path traversal and absolute-path local file read without unsafe mode

## Summary
Severity: Medium
Advisory: GHSA-hgjq-p8cr-gg4h
CVE: CVE-2026-34730
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-hgjq-p8cr-gg4h
Type: github-advisory

## Affected
- PyPI: `copier` — affected >=0 <9.14.1

## Details
### Summary

Copier's `_external_data` feature allows a template to load YAML files using template-controlled paths. The documentation describes these values as relative paths from the subproject destination, so relative paths themselves appear to be part of the intended feature model.

However, the current implementation also allows destination-external reads, including:

- Parent-directory paths such as `../secret.yml`
- Absolute paths such as `/tmp/secret.yml`

and then exposes the parsed contents in rendered output.

This is possible without `--UNSAFE`, which makes the behavior potentially dangerous when Copier is run against untrusted templates. I am not certain this is unintended behavior, but it is security-sensitive and appears important to clarify.

### Details

The relevant flow is:

1. A template defines `_external_data`
2. Copier renders the configured path string
3. Copier calls `load_answersfile_data(dst_path, rendered_path, warn_on_missing=True)`
4. `load_answersfile_data()` opens `Path(dst_path, answers_file)` directly
5. Parsed YAML becomes available as `_external_data.<name>` during rendering

Relevant code:

- <https://github.com/copier-org/copier/blob/7aa7021bd73797c982492bac3535515d4484fdb7/copier/_main.py#L329-L332>
- <https://github.com/copier-org/copier/blob/7aa7021bd73797c982492bac3535515d4484fdb7/copier/_user_data.py#L584-L592>

The sink is:

```python
with Path(dst_path, answers_file).open("rb") as fd:
    return yaml.safe_load(fd)
```

There is no containment check to ensure the resulting path stays inside the subproject destination.

This is notable because Copier already blocks other destination-escape paths. Normal render-path traversal outside the destination is expected to raise `ForbiddenPathError`, and that behavior is explicitly covered by existing tests in <https://github.com/copier-org/copier/blob/7aa7021bd73797c982492bac3535515d4484fdb7/tests/test_copy.py#L1289-L1332>. `_external_data` does not apply an equivalent containment check.

The public documentation describes `_external_data` values as relative paths "from the subproject destination" in <https://github.com/copier-org/copier/blob/7aa7021bd73797c982492bac3535515d4484fdb7/docs/configuring.md#L944-L1005>, with examples using `.copier-answers.yml` and `.secrets.yaml`. That clearly supports relative-path usage, but it does not clearly communicate that a template may escape the destination with `../...` or read arbitrary absolute paths. Because this behavior also works without `--UNSAFE`, it seems worth clarifying whether destination-external reads are intended, and if so, whether they should be documented as security-sensitive behavior.

### PoC

#### PoC 1: `_external_data` reads outside the destination with `../`

```sh
mkdir src dst
echo 'token: topsecret' > secret.yml

printf '%s\n' '_external_data:' '  secret: ../secret.yml' > src/copier.yml
printf '%s\n' '{{ _external_data.secret.token }}' > src/leak.txt.jinja

copier copy --overwrite src dst
cat dst/leak.txt
```

Expected output:

```text
topsecret
```

#### PoC 2: `_external_data` reads an absolute path

```sh
mkdir abs-src abs-dst
echo 'token: abssecret' > absolute-secret.yml

printf '%s\n' '_external_data:' "  secret: $(pwd)/absolute-secret.yml" > abs-src/copier.yml
printf '%s\n' '{{ _external_data.secret.token }}' > abs-src/leak.txt.jinja

copier copy --overwrite abs-src abs-dst
cat abs-dst/leak.txt
```

Expected output:

```text
abssecret
```

### Impact

If untrusted templates are in scope, a malicious template can read attacker-chosen YAML-parseable local files that are accessible to the user running Copier and expose their contents in rendered output.

Practical impact:

- Destination-external local file read
- Disclosure of YAML/JSON/plain-text-like secrets if they parse successfully under `yaml.safe_load`
- Possible without `--UNSAFE`

## References
- https://github.com/copier-org/copier/security/advisories/GHSA-hgjq-p8cr-gg4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34730
- https://github.com/copier-org/copier/commit/5413062eb17b73dc885f5e645cdc161e69ef641b
- https://github.com/copier-org/copier
- https://github.com/copier-org/copier/releases/tag/v9.14.1
