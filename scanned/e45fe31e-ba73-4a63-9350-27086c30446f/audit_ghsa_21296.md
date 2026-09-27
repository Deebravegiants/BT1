# [H] Poetry vulnerable to Untrusted Search Path leading to Local Code Execution on Windows

## Summary
Severity: High
Advisory: GHSA-j4j9-7hg9-97g6
CVE: CVE-2022-36070
CWE: CWE-426
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-j4j9-7hg9-97g6
Type: github-advisory

## Affected
- PyPI: `poetry` — affected >=0 <1.1.9

## Details
### Observation

To handle dependencies that come from a Git repository, Poetry executes various commands, e.g. `git config`. These commands are being executed using the executable’s name and not its absolute path.

This can lead to the execution of untrusted code due to the way Windows resolves executable names to paths. Unlike Linux-based operating systems, Windows searches for the executable in the current directory first and looks in the paths that are defined in the `PATH` environment variable afterward. If the current directory contains unknown and thus potentially malicious files, the directory could contain an executable named `git.exe` which would be executed by Poetry.

Poetry calls executables by name when handling dependencies from Git. Note that there might be even more places where Poetry calls executables by name.

### Impact

This vulnerability can lead to Arbitrary Code Execution, which would lead to the takeover of the system. If a developer is exploited, the attacker could steal credentials or persist their access. If the exploit happens on a server, the attackers could use their access to attack other internal systems.
Since this vulnerability requires a fair amount of user interaction, it is not as dangerous as a remotely exploitable one. However, it still puts developers at risk when dealing with untrusted files in a way they think is safe, because the exploit still works when the victim tries to make
 
sure nothing can happen, e.g. by checking that the referenced Git dependency is not malicious and points to a trusted Git repository.
The victim could also not protect themself by vetting any Git or Poetry config files that might be present in the directory, because the behavior is undocumented. This kind of attack vector has been used in the past to target security researchers by sending them projects to collaborate on, so we believe that there is a non-negligible risk.

### Patches

1.1.9 || 1.2.0b1

### Remediation

Upgrade to version 1.1.9 || 1.2.0b1

### References

[Fix PR](https://github.com/python-poetry/poetry-core/pull/204)

### For more information

If you have any questions or comments about this advisory:
* Email us at [security@python-poetry.org](mailto:security@python-poetry.org)

## References
- https://github.com/python-poetry/poetry/security/advisories/GHSA-j4j9-7hg9-97g6
- https://nvd.nist.gov/vuln/detail/CVE-2022-36070
- https://github.com/pypa/advisory-database/tree/main/vulns/poetry/PYSEC-2022-43179.yaml
- https://github.com/python-poetry/poetry
- https://github.com/python-poetry/poetry/releases/tag/1.1.9
- https://github.com/python-poetry/poetry/releases/tag/1.2.0b1
