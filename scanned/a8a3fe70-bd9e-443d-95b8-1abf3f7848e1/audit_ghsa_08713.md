# [M] Microsoft APM: Windows absolute-path tar member overwrite during legacy-bundle probing in `apm install`

## Summary
Severity: Medium
Advisory: GHSA-mq5j-pw29-jcv3
CVE: CVE-2026-46383
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-mq5j-pw29-jcv3
Type: github-advisory

## Affected
- PyPI: `apm-cli` — affected >=0 <0.13.0

## Details
### Summary

Microsoft APM contains a Windows-specific archive extraction boundary failure in the legacy-bundle probe used by `apm install <bundle>` on supported Python 3.10 and 3.11 runtimes. When `apm install` is given a local `.tar.gz` that is not recognized as a plugin-format bundle, APM probes whether it is a legacy `--format apm` bundle. On Python versions earlier than 3.12, that probe extracts untrusted tar members with raw `tar.extractall()` without rejecting Windows absolute member names such as `D:/...`.

This issue is still present on the latest `main` commit at review time (`2b7a931d58a73cbfc0bcf086cea332d204075e27`) and on the latest release (`v0.12.4`). In both cases, a crafted legacy-looking tarball caused an external file to be created or overwritten outside the temporary extraction root before `apm install` finished rejecting the bundle with the expected legacy-format usage error.

This report is scoped narrowly to Windows installations running Python 3.10 or 3.11.

### Details

The broken trust boundary is the boundary between an untrusted local bundle artifact and the host filesystem state that APM is allowed to modify while probing that artifact. The attacker-controlled input is the tar member name inside the `.tar.gz` bundle. A crafted archive can include a member whose name is a Windows absolute path such as `D:/apm/run-main-install/outside/legacy-probe-outside-main.txt`.

The current install caller path still reaches the legacy probe for `.tar.gz` inputs that are not recognized as plugin-format bundles. In `src/apm_cli/commands/install.py`, the local-bundle branch first calls `detect_local_bundle()`. If the path exists, is a tarball, and is not recognized as a plugin-format bundle, the caller still invokes `_looks_like_legacy_apm_bundle()` to distinguish a legacy bundle from an arbitrary tarball and to choose the error message.

The root cause is in `src/apm_cli/bundle/local_bundle.py`. `_looks_like_legacy_apm_bundle()`:

- opens the tarball,
- rejects only symlink and hardlink members,
- and on Python versions earlier than 3.12 calls raw `tar.extractall(tmp)`.

That helper does not reject Windows absolute member names and does not perform the Windows-aware containment checks already present elsewhere in the same module.

This is particularly clear because the adjacent `detect_local_bundle()` path in the same file already contains safer pre-extraction validation. It rejects:

- `PureWindowsPath(name).drive`
- `PureWindowsPath(name).is_absolute()`
- path traversal via `validate_path_segments(...)`

That safer validation is not reused by `_looks_like_legacy_apm_bundle()`.

On Python versions earlier than 3.12, `_looks_like_legacy_apm_bundle()` performs extraction before legacy-format rejection is raised, so archive member names become filesystem writes during bundle classification rather than during an accepted install step. The write occurs before command rejection because the legacy probe must extract the tarball in order to look for `apm.lock.yaml` at the bundle root and confirm that `plugin.json` is absent. As a result, the out-of-root write happens during classification, before the caller raises the legacy-format usage error.

The issue is not limited to creating new files. On both latest `main` and latest release, the same vulnerable path overwrote an already-existing writable target file with attacker-controlled contents before the command finished legacy-format rejection. It was further verified the same overwrite primitive against a pre-existing project workflow file at `.github/workflows/ci.yml`, replacing its YAML contents before rejection.

This is a security issue rather than intended package-manager behavior. The user is asking APM to inspect or install a local bundle. The expected behavior is that bundle contents are handled within the extraction sandbox used for that operation. Writing to an arbitrary host path outside the extraction root during pre-install probing is not part of expected local-bundle behavior, and it happens even when APM ultimately rejects the tarball.

This issue is also distinct from the prior public APM plugin path-escape issue. The prior public issue involved manifest-controlled path escape during plugin normalization in `plugin_parser.py`, where attacker-controlled manifest entries were resolved outside the plugin root during install. This issue is different in input, timing, and code path: it is an archive-member extraction bug in `src/apm_cli/bundle/local_bundle.py` during legacy-bundle probing, before bundle classification completes and before `apm install` rejects the bundle. No manifest processing is required to trigger it.

As additional same-family scope information, the same Windows absolute-path extraction weakness is also reproducible in apm unpack.In `src/apm_cli/bundle/unpacker.py`, the unpacker rejects `/` and `..` but still misses Windows absolute tar member names before calling `tar.extractall()` on Python versions earlier than 3.12. Because `apm unpack` is deprecated, I am not presenting it as a second standalone vulnerability title; I am including it only as additional affected surface from the same validation family.

### PoC

Validation environment used for the included proof:

- Windows 11 Pro
- Python 3.11.9 x64
- Latest `main` commit: `2b7a931d58a73cbfc0bcf086cea332d204075e27`
- Latest release commit: `6aceef72be490a9c716547f600a2659f3f2826b7` (`v0.12.4`)

Minimal malicious archive contents:

- `bundle/apm.lock.yaml`
- `D:/apm/run-main-install/outside/legacy-probe-outside-main.txt`

The first member makes the archive look like a legacy APM bundle. The second member proves the out-of-root write. The outside target path must be writable by the user running APM. The proof uses a user-controlled directory for that reason.

One straightforward way to build this input is to use Python's `tarfile` module directly and add:

- `bundle/apm.lock.yaml`
- `TarInfo("D:/apm/run-main-install/outside/legacy-probe-outside-main.txt")`

with file content such as:

```text
outside write via install main
```

Reproduction steps for latest `main`:

1. Check out `microsoft/apm` at `2b7a931d58a73cbfc0bcf086cea332d204075e27`.
2. Use a real Windows Python 3.11 runtime.
3. Ensure the `apm_cli` import resolves to the checked-out tree.
4. Create the malicious legacy-looking tarball described above.
5. Run:

```powershell
python -m apm_cli.cli install D:\apm\run-main-install\input\legacy-bundle.tar.gz
```

Expected safe behavior:

- APM rejects the tarball without creating or overwriting any host file outside the temporary extraction root.

Observed result on latest `main`:

- the import path resolved to the checked-out `main` tree,
- the command ended with the expected legacy-format rejection,
- the process exit code was `2`,
- and the file below had already been created outside the temporary extraction root:

```text
D:\apm\run-main-install\outside\legacy-probe-outside-main.txt
```

The file contained:

```text
outside write via install main
```

I also verified overwrite, not just creation, by pre-creating a writable target file and then running the same install path. The existing file contents changed from `ORIGINAL-MAIN` to `OVERWRITTEN-MAIN` before rejection.

I further verified overwrite of a pre-existing project workflow file. Before the run, the target file contained:

```yaml
name: safe
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo safe
```

After the run, the same file contained attacker-controlled replacement YAML:

```yaml
name: overwritten
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo overwritten-by-archive
```

Observed command output on latest `main`:

```text
[!] Install interrupted after 0.0s.
Usage: python -m apm_cli.cli install [OPTIONS] [PACKAGES]...
Try 'python -m apm_cli.cli install --help' for help.

Error: 'D:\apm\run-main-install\input\legacy-bundle.tar.gz' was packed with '--format apm' (legacy format). 'apm install <bundle>' requires the plugin format. Repack with 'apm pack --format plugin --archive', or use 'apm unpack' to deploy the legacy bundle.
```

Reproduction steps for latest release `v0.12.4`:

1. Check out tag `v0.12.4` / commit `6aceef72be490a9c716547f600a2659f3f2826b7`.
2. Use the same Windows Python 3.11 runtime.
3. Ensure the `apm_cli` import resolves to the `v0.12.4` tree.
4. Create the same malicious tarball shape, for example with:

```text
D:/apm/run-release-install/outside/legacy-probe-outside-release.txt
```

5. Run:

```powershell
python -m apm_cli.cli install D:\apm\run-release-install\input\legacy-bundle.tar.gz
```

Observed result on latest release:

- the import path resolved to the checked-out `v0.12.4` tree,
- the command ended with the expected legacy-format rejection,
- the process exit code was `2`,
- and the file below had already been created outside the temporary extraction root:

```text
D:\apm\run-release-install\outside\legacy-probe-outside-release.txt
```

The file contained:

```text
outside write via install release
```

I also verified overwrite, not just creation, on the latest release by pre-creating a writable target file. The existing file contents changed from `ORIGINAL-RELEASE` to `OVERWRITTEN-RELEASE` before rejection. The same workflow-file overwrite pattern was also reproducible on the latest release.

Observed command output on latest release:

```text
[!] Install interrupted after 0.0s.
Usage: python -m apm_cli.cli install [OPTIONS] [PACKAGES]...
Try 'python -m apm_cli.cli install --help' for help.

Error: 'D:\apm\run-release-install\input\legacy-bundle.tar.gz' was packed with '--format apm' (legacy format). 'apm install <bundle>' requires the plugin format. Repack with 'apm pack --format plugin --archive', or use 'apm unpack' to deploy the legacy bundle.
```

Additional same-family affected surface:

- `apm unpack` on latest `main` and latest release also created an outside file when given a tarball containing a Windows absolute member name.
- In that path the command completed successfully with exit code `0`, which further confirms that the Windows absolute-path validation gap is present outside the primary install probe as well.

### Impact

This is an arbitrary local file overwrite outside the intended extraction root during a current APM install path. The impacted population is Windows users running APM on supported Python 3.10 or 3.11 runtimes. The attacker capability required is the ability to supply a crafted local bundle and induce the victim to run `apm install` on it.

The strongest demonstrated real-world consequence is attacker-controlled overwrite of an existing writable file at an attacker-selected Windows path outside the extraction root, using the privileges of the user running APM. An overwrite of a project-controlled GitHub Actions workflow file with attacker-controlled YAML before rejection was verified.  Workflow execution from this report hasn't been claimed; the demonstrated consequence is high-integrity modification of a trusted automation file outside the intended extraction boundary.

The issue is currently reachable on:

- latest `main` at `2b7a931d58a73cbfc0bcf086cea332d204075e27`
- latest release `v0.12.4`

### Mitigation

1. Reuse the existing pre-extraction validation already implemented in `detect_local_bundle()` for `_looks_like_legacy_apm_bundle()`.
2. Reject Windows absolute member names before any extraction step.
3. Apply equivalent Windows absolute-path validation to the unpacker in `src/apm_cli/bundle/unpacker.py`.
4. Add regression tests for:
   - Windows absolute member paths in the legacy-bundle probe path
   - Windows absolute member paths in the unpack path
   - confirmation that no host write occurs before the legacy-format rejection is raised

### Attachment
[apm-legacy-probe-windows-absolute-path-write-20260511.zip](https://github.com/user-attachments/files/27578792/apm-legacy-probe-windows-absolute-path-write-20260511.zip)

## References
- https://github.com/microsoft/apm/security/advisories/GHSA-mq5j-pw29-jcv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-46383
- https://github.com/microsoft/apm/commit/77d1dda8303c8d7ccb6148788a6274fdece98499
- https://github.com/microsoft/apm
- https://github.com/microsoft/apm/releases/tag/v0.13.0
