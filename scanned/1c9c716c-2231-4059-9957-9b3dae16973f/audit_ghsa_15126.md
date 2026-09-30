# [H] Untrusted search path under some conditions on Windows allows arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-2mqj-m65w-jghx
CVE: CVE-2024-22190
CWE: CWE-426
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-2mqj-m65w-jghx
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.41

## Details
### Summary

This issue exists because of an incomplete fix for CVE-2023-40590. On Windows, GitPython uses an untrusted search path if it uses a shell to run `git`, as well as when it runs `bash.exe` to interpret hooks. If either of those features are used on Windows, a malicious `git.exe` or `bash.exe` may be run from an untrusted repository.

### Details

Although GitPython often avoids executing programs found in an untrusted search path since 3.1.33, two situations remain where this still occurs. Either can allow arbitrary code execution under some circumstances.

#### When a shell is used

GitPython can be told to run `git` commands through a shell rather than as direct subprocesses, by passing `shell=True` to any method that accepts it, or by both setting `Git.USE_SHELL = True` and not passing `shell=False`. Then the Windows `cmd.exe` shell process performs the path search, and GitPython does not prevent that shell from finding and running `git` in the current directory.

When GitPython runs `git` directly rather than through a shell, the GitPython process performs the path search, and currently omits the current directory by setting `NoDefaultCurrentDirectoryInExePath` in its own environment during the `Popen` call. Although the `cmd.exe` shell will honor this environment variable when present, GitPython does not currently pass it into the shell subprocess's environment.

Furthermore, because GitPython sets the subprocess CWD to the root of a repository's working tree, using a shell will run a malicious `git.exe` in an untrusted repository even if GitPython itself is run from a trusted location.

This also applies if `Git.execute` is called directly with `shell=True` (or after `Git.USE_SHELL = True`) to run any command.

#### When hook scripts are run

On Windows, GitPython uses `bash.exe` to run hooks that appear to be scripts. However, unlike when running `git`, no steps are taken to avoid finding and running `bash.exe` in the current directory.

This allows the author of an untrusted fork or branch to cause a malicious `bash.exe` to be run in some otherwise safe workflows. An example of such a scenario is if the user installs a trusted hook while on a trusted branch, then switches to an untrusted feature branch (possibly from a fork) to review proposed changes. If the untrusted feature branch contains a malicious `bash.exe` and the user's current working directory is the working tree, and the user performs an action that runs the hook, then although the hook itself is uncorrupted, it runs with the malicious `bash.exe`.

Note that, while `bash.exe` is a shell, this is a separate scenario from when `git` is run using the unrelated Windows `cmd.exe` shell.

### PoC

On Windows, create a `git.exe` file in a repository. Then create a `Repo` object, and call any method through it (directly or indirectly) that supports the `shell` keyword argument with `shell=True`:

```powershell
mkdir testrepo
git init testrepo
cp ... testrepo git.exe # Replace "..." with any executable of choice.
python -c "import git; print(git.Repo('testrepo').git.version(shell=True))"
```

The `git.exe` executable in the repository directory will be run.

Or use no `Repo` object, but do it from the location with the `git.exe`:

```powershell
cd testrepo
python -c "import git; print(git.Git().version(shell=True))"
```

The `git.exe` executable in the current directory will be run.

For the scenario with hooks, install a hook in a repository, create a `bash.exe` file in the current directory, and perform an operation that causes GitPython to attempt to run the hook:

```powershell
mkdir testrepo
cd testrepo
git init
mv .git/hooks/pre-commit.sample .git/hooks/pre-commit
cp ... bash.exe # Replace "..." with any executable of choice.
echo "Some text" >file.txt
git add file.txt
python -c "import git; git.Repo().index.commit('Some message')"
```

The `bash.exe` executable in the current directory will be run.

### Impact

The greatest impact is probably in applications that set `Git.USE_SHELL = True` for historical reasons. (Undesired console windows had, in the past, been created in some kinds of applications, when it was not used.) Such an application may be vulnerable to arbitrary code execution from a malicious repository, even with no other exacerbating conditions. This is to say that, if a shell is used to run `git`, the full effect of CVE-2023-40590 is still present. Furthermore, as noted above, running the application itself from a trusted directory is not a sufficient mitigation.

An application that does not direct GitPython to use a shell to run `git` subprocesses thus avoids most of the risk. However, there is no such straightforward way to prevent GitPython from running `bash.exe` to interpret hooks. So while the conditions needed for that to be exploited are more involved, it may be harder to mitigate decisively prior to patching.

### Possible solutions

A straightforward approach would be to address each bug directly:

- When a shell is used, pass `NoDefaultCurrentDirectoryInExePath` into the subprocess environment, because in that scenario the subprocess is the `cmd.exe` shell that itself performs the path search.
- Set `NoDefaultCurrentDirectoryInExePath` in the GitPython process environment during the `Popen` call made to run hooks with a `bash.exe` subprocess.

These need only be done on Windows.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-2mqj-m65w-jghx
- https://nvd.nist.gov/vuln/detail/CVE-2024-22190
- https://github.com/gitpython-developers/GitPython/pull/1792
- https://github.com/gitpython-developers/GitPython/commit/ef3192cc414f2fd9978908454f6fd95243784c7f
- https://github.com/gitpython-developers/GitPython
- https://github.com/pypa/advisory-database/tree/main/vulns/gitpython/PYSEC-2024-4.yaml
