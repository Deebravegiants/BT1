# [H] pydicom has a path traversal in FileSet/DICOMDIR ReferencedFileID allows file access outside the File-set root

## Summary
Severity: High
Advisory: GHSA-v856-2rf8-9f28
CVE: CVE-2026-32711
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-v856-2rf8-9f28
Type: github-advisory

## Affected
- PyPI: `pydicom` — affected >=3.0.0 <3.0.2
- PyPI: `pydicom` — affected >=0 <2.4.5

## Details
### Summary
A crafted `DICOMDIR` can set `ReferencedFileID` to a path outside the File-set root. `pydicom` resolves the path only to confirm that it exists, but does not verify that the resolved path remains under the File-set root. Subsequent public `FileSet` operations such as `copy()`, `write()`, and `remove()+write(use_existing=True)` use that unchecked path in file I/O operations. This allows arbitrary file read/copy and, in some flows, move/delete outside the File-set root.

### Details
Verified on `pydicom 3.1.0.dev0`.

Relevant logic is in `src/pydicom/fileset.py`:

- `RecordNode._file_id` converts `ReferencedFileID` directly to `Path(...)`
- `FileSet.load()` checks only `(root / file_id).resolve(strict=True)` to confirm existence
- `FileSet.load()` does not verify that the final resolved path is contained within the File-set root
- `FileInstance.path` returns `self.file_set.path / self.node._file_id`
- `FileSet.copy()` uses `shutil.copyfile(instance.path, dst)`
- `FileSet.write()` uses `Path(instance.path).unlink()` and `shutil.move(...)`

Because there is no containment check such as `resolved.relative_to(root.resolve(strict=True))`, a malicious `DICOMDIR` can reference:

- absolute paths such as `/etc/passwd`
- traversal paths such as `../...`
- syntactically conformant file IDs that escape via symlinks

This is not limited to obviously invalid VR input. Even when `pydicom` emits warnings for invalid `ReferencedFileID` values, the operation is not blocked. I also confirmed a symlink-based variant using a conformant file ID.

A realistic server-side scenario is:

1. a user uploads a DICOM File-set zip
2. the server loads the uploaded `DICOMDIR` using `FileSet`
3. the server re-exports or reorganizes the File-set using `FileSet.copy()` or `FileSet.write()`
4. a server-local file referenced by the malicious `DICOMDIR` is included in the exported result

### PoC
Minimal reproduction:

1. Copy a sample File-set that contains a valid `DICOMDIR`
2. Modify one `DirectoryRecordSequence` item so that `ReferencedFileID = "/etc/passwd"` (or `/tmp/secret.txt`)
3. Load it with `FileSet(ds)` or `FileSet(path_to_dicomdir)`
4. Call `FileSet.copy(new_root)`
5. Observe that the exported File-set contains the contents of the referenced external file

Example:

```python
from pathlib import Path
from tempfile import mkdtemp
import shutil
from pydicom import dcmread
from pydicom.fileset import FileSet

base = Path("src/pydicom/data/test_files/dicomdirtests")
root = Path(mkdtemp(prefix="fsroot_"))
out = Path(mkdtemp(prefix="fsout_"))

shutil.copy2(base / "DICOMDIR", root / "DICOMDIR")
for d in ("77654033", "98892003", "98892001"):
    shutil.copytree(base / d, root / d)

ds = dcmread(root / "DICOMDIR")
item = next(x for x in ds.DirectoryRecordSequence if "ReferencedFileID" in x)
item.ReferencedFileID = "/etc/passwd"

fs = FileSet(ds)
fs.copy(out)
```

I also verified the issue in a simple web import/export demo where an uploaded malicious File-set caused /etc/passwd to be copied into the exported result.

If useful, I can provide the exact malicious sample and the demo environment separately.

### Impact
This is a path traversal / root containment bypass in FileSet handling.

Observed impact:

arbitrary file read/copy outside the File-set root via FileSet.copy()
arbitrary file move outside the File-set root via FileSet.write()
arbitrary file delete outside the File-set root via FileSet.remove(...); write(use_existing=True)
Affected applications are those that accept untrusted DICOMDIR / File-set input and then call public FileSet workflows such as load(), copy(), write(), or remove().

A realistic impact is server-side file disclosure in import/export workflows.

## References
- https://github.com/pydicom/pydicom/security/advisories/GHSA-v856-2rf8-9f28
- https://nvd.nist.gov/vuln/detail/CVE-2026-32711
- https://github.com/pydicom/pydicom/commit/6414f01a053dff925578799f5a7208d2ae585e82
- https://github.com/pydicom/pydicom
- https://github.com/pydicom/pydicom/releases/tag/v3.0.2
