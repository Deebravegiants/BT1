# [M] Copier `_subdirectory` allows template root escape via parent-directory traversal

## Summary
Severity: Medium
Advisory: GHSA-85v3-4m8g-hrh6
CVE: CVE-2026-34726
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-85v3-4m8g-hrh6
Type: github-advisory

## Affected
- PyPI: `copier` — affected >=0 <9.14.1

## Details
### Summary

Copier's `_subdirectory` setting is documented as the subdirectory to use as the template root. However, the current implementation accepts parent-directory traversal such as `..` and uses it directly when selecting the template root.

As a result, a template can escape its own directory and make Copier render files from the parent directory without `--UNSAFE`.

### Details

The relevant code path is:

1. the template defines `_subdirectory`
2. Copier renders that string
3. `template_copy_root` returns `self.template.local_abspath / subdir`
4. Copier walks that directory as the template root

Relevant code:

- <https://github.com/copier-org/copier/blob/7aa7021bd73797c982492bac3535515d4484fdb7/copier/_main.py#L1056-L1062>
- <https://github.com/copier-org/copier/blob/7aa7021bd73797c982492bac3535515d4484fdb7/copier/_template.py#L504-L513>

The effective sink is:

```python
subdir = self._render_string(self.template.subdirectory) or ""
return self.template.local_abspath / subdir
```

There is no check that the resulting path stays inside the template directory.

The documentation for `_subdirectory` describes it as:

> Subdirectory to use as the template root when generating a project.

and explains it as a way to separate template metadata from template source code:

<https://github.com/copier-org/copier/blob/7aa7021bd73797c982492bac3535515d4484fdb7/docs/configuring.md#L1582-L1646>

That description fits values like `template` or `poetry`, but not `..`.

### PoC

#### PoC 1: `_subdirectory: ..` escapes to the parent directory

```sh
mkdir -p root/template dst
echo 'loot' > root/loot.txt
printf '%s\n' '_subdirectory: ..' > root/template/copier.yml

copier copy --overwrite root/template dst
find dst -maxdepth 3 -type f | sort
cat dst/loot.txt
```

Expected output includes:

```text
dst/loot.txt
dst/template/copier.yml
loot
```

This shows Copier is rendering from `root/` rather than from `root/template/`.

### Impact

If a user runs Copier on an untrusted template, that template can change the effective template root and make Copier render files from outside the intended template directory.

Practical impact:

- template-root escape via `..`
- rendering of parent-directory files that were not meant to be part of the template
- possible without `--UNSAFE`

## References
- https://github.com/copier-org/copier/security/advisories/GHSA-85v3-4m8g-hrh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-34726
- https://github.com/copier-org/copier/commit/cb80a3ffc9c3787de3ed837e04ca29a0ff8ca3df
- https://github.com/copier-org/copier
- https://github.com/copier-org/copier/releases/tag/v9.14.1
