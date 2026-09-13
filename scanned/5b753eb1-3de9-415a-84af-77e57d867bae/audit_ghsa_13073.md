# [H] GitPython untrusted search path on Windows systems leading to arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-wfm5-v35h-vwf4
CVE: CVE-2023-40590
CWE: CWE-426
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-wfm5-v35h-vwf4
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.33

## Details
### Summary

When resolving a program, Python/Windows look for the current working directory, and after that the PATH environment (see big warning in https://docs.python.org/3/library/subprocess.html#popen-constructor). GitPython defaults to use the `git` command, if a user runs GitPython from a repo has a `git.exe` or `git` executable, that program will be run instead of the one in the user's `PATH`.

### Details

This is more of a problem on how Python interacts with Windows systems, Linux and any other OS aren't affected by this. But probably people using GitPython usually run it from the CWD of a repo.

The execution of the `git` command happens in

https://github.com/gitpython-developers/GitPython/blob/1c8310d7cae144f74a671cbe17e51f63a830adbf/git/cmd.py#L277 

https://github.com/gitpython-developers/GitPython/blob/1c8310d7cae144f74a671cbe17e51f63a830adbf/git/cmd.py#L983-L996

And there are other commands executed that should probably be aware of this problem.

### PoC

On a Windows system, create a `git.exe` or `git` executable in any directory, and import or run GitPython from that directory

```
python -c "import git"
```

The git executable from the current directory will be run.

### Impact

An attacker can trick a user to download a repository with a malicious `git` executable, if the user runs/imports GitPython from that directory, it allows the attacker to run any arbitrary commands.

### Possible solutions
 
- Default to an absolute path for the git program on Windows, like `C:\\Program Files\\Git\\cmd\\git.EXE` (default git path installation).
- Require users to set the `GIT_PYTHON_GIT_EXECUTABLE` environment variable on Windows systems.
- Make this problem prominent in the documentation and advise users to never run GitPython from an untrusted repo, or set the `GIT_PYTHON_GIT_EXECUTABLE` env var to an absolute path.
- Resolve the executable manually by only looking into the `PATH` environment variable (suggested by @Byron)

---

> [!NOTE]
> This vulnerability was reported via email, and it was decided to publish it here and make it public, so the community is aware of it, and a fix can be provided.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-wfm5-v35h-vwf4
- https://nvd.nist.gov/vuln/detail/CVE-2023-40590
- https://github.com/gitpython-developers/GitPython/issues/1635
- https://github.com/gitpython-developers/GitPython/pull/1636
- https://github.com/gitpython-developers/GitPython/commit/8b75434e2c8a082cdeb4971cc6f0ee2bafec45bc
- https://docs.python.org/3/library/subprocess.html#popen-constructor
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.33
- https://github.com/pypa/advisory-database/tree/main/vulns/gitpython/PYSEC-2023-161.yaml
