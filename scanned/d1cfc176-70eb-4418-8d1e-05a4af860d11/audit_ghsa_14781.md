# [C] Remote Code Execution via path traversal bypass in lollms

## Summary
Severity: Critical
Advisory: GHSA-mvrm-fh8q-6wr2
CVE: CVE-2024-5443
CWE: CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-22
Source: https://github.com/advisories/GHSA-mvrm-fh8q-6wr2
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=5.9.0 <9.5.1

## Details
CVE-2024-4320 describes a vulnerability in the parisneo/lollms software, specifically within the `ExtensionBuilder().build_extension()` function. The vulnerability arises from the `/mount_extension` endpoint, where a path traversal issue allows attackers to navigate beyond the intended directory structure. This is facilitated by the `data.category` and `data.folder` parameters accepting empty strings (`""`), which, due to inadequate input sanitization, can lead to the construction of a `package_path` that points to the root directory. Consequently, if an attacker can create a `config.yaml` file in a controllable path, this path can be appended to the `extensions` list and trigger the execution of `__init__.py` in the current directory, leading to remote code execution. The vulnerability affects versions from 5.9.0, and has been addressed in version 9.5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5443
- https://github.com/parisneo/lollms/commit/2d0c4e76be93195836ecd0948027e791b8a2626f
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/db52848a-4dbe-4110-a981-03739834bf45
