# [M] setuptools: MANIFEST.in exclusion bypass in sdist via Unicode normalization collision (NFC/NFD) on macOS APFS/HFS+

## Summary
Severity: Medium
Advisory: GHSA-h35f-9h28-mq5c
CVE: CVE-2026-59890
CWE: CWE-176, CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-h35f-9h28-mq5c
Type: github-advisory

## Affected
- PyPI: `setuptools` — affected >=0 <83.0.0

## Details
## Summary

When building a source distribution (`python -m build --sdist` / `setup.py sdist`), setuptools' `FileList` applies `MANIFEST.in` directives (`exclude`, `global-exclude`, `recursive-exclude`, `prune`) by matching a compiled glob against on-disk file names **byte-for-byte, with no Unicode normalization**. On normalization-preserving filesystems (notably macOS APFS and HFS+), a file written in NFD and a `MANIFEST.in` rule written in NFC refer to the same file but are byte-distinct, so the exclusion silently fails to match. A file the maintainer intended to exclude is then packed into the `.tar.gz` and, if published, uploaded to the public, immutable PyPI index.

## Details

File names in `FileList.files` come from `os.walk` (`setuptools/_distutils/filelist.py`, `_find_all_simple`), so on APFS a file written NFD is offered to the matcher in NFD, while the `MANIFEST.in` pattern carries the author's editor form (typically NFC). The matching path performs no canonicalization:

```python
# setuptools/command/egg_info.py  (FileList.global_exclude)
def global_exclude(self, pattern):
    match = translate_pattern(os.path.join('**', pattern))   # fnmatch.translate -> regex, no NFC/NFD
    return self._remove_files(match.match)                   # byte-level regex over raw os.walk names
```

A rule written NFC (`café` = `63 61 66 c3 a9`) does not match an on-disk name written NFD (`café` = `63 61 66 65 cc 81`), even though the filesystem treats the two as one file.

A `unicodedata.normalize('NFD', ...)` helper exists in `setuptools/unicode_utils.py` (`decompose()`), but it is **never called in the manifest matching path**, so neither the pattern nor the walked path is normalized before matching. The only normalization in this area, `EggInfoCommand._manifest_normalize`, uses `filesys_decode` (bytes→str decode only, no NFC/NFD) and runs when writing `SOURCES.txt`, after matching has already occurred.

## Impact

`MANIFEST.in` exclusions are the documented mechanism maintainers use to keep secrets, local configs, and private fixtures out of the published sdist. A non-ASCII excluded file may be published to the public, immutable PyPI index despite the rule — an irreversible disclosure with no visual cue (NFC and NFD forms render identically). Exposure is filesystem-dependent and most relevant on macOS APFS/HFS+, where many maintainers build and publish. Pure-ASCII rules are unaffected.

## Proof of concept

With a project containing `MANIFEST.in`:

```
global-include *.txt *.json
global-exclude secret_café.txt    # rule saved NFC
```

and an on-disk file `secret_café.txt` written in NFD, `python -m build --sdist` packs the secret file into the resulting `.tar.gz`, while an ASCII control file excluded by the same directive is correctly dropped — isolating the bypass to the NFC-pattern vs. NFD-name mismatch. Reproduced on macOS APFS with setuptools 82.0.1.

## Remediation

Normalize both the walked path and each `MANIFEST.in` pattern to a single canonical form before matching, in both `setuptools/command/egg_info.py` (`FileList`) and the vendored `setuptools/_distutils/filelist.py`. For an exclusion list, err toward excluding more, and document that `MANIFEST.in` matching is normalization-insensitive on macOS.

## Credit

Reported by Tomas Illuminati. Coordinated via CERT/CC VINCE VU#604762.

## References
- https://github.com/pypa/setuptools/security/advisories/GHSA-h35f-9h28-mq5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-59890
- https://github.com/pypa/setuptools/commit/dd9f436a36486b4cb8a4c70a2321548b0be09b8f
- https://github.com/pypa/advisory-database/tree/main/vulns/setuptools/PYSEC-2026-3447.yaml
- https://github.com/pypa/setuptools
- https://github.com/pypa/setuptools/releases/tag/v83.0.0
