# [H] PDM Trojan Lockfile

## Summary
Severity: High
Advisory: GHSA-j44v-mmf2-xvm9
CVE: CVE-2023-45805
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-20
Source: https://github.com/advisories/GHSA-j44v-mmf2-xvm9
Type: github-advisory

## Affected
- PyPI: `pdm` — affected >=0

## Details
### Summary
It's possible to craft a malicious `pdm.lock` file that could allow e.g. an insider or a malicious open source project to appear to depend on a trusted PyPI project, but actually install another project.

### Details
Project `foo` can be targeted by creating the project `foo-2` and uploading the file `foo-2-2.tar.gz` to pypi.org. PyPI will see this as project `foo-2` version `2`, while PDM will see this as project `foo` version `2-2`. The version must only be [parseable as a version](https://github.com/frostming/unearth/blob/eca170d9370ac5032f2e497ee9b1b63823d3fe0f/src/unearth/evaluator.py#L215-L229) (and the filename must be a prefix of the project name), but it's [not verified to match the version being installed](https://github.com/pdm-project/pdm/blob/45d1dfa47d4900c14a31b9bb761e4c46eb5c9442/src/pdm/models/candidates.py#L98-L99). (Version `2-2` is also not a valid [normalized version per PEP 440](https://peps.python.org/pep-0440/#post-release-spelling).)

Matching the project name exactly (not just prefix) would fix the issue. The version should also be verified to avoid version downgrade attacks.

### PoC
Example `pdm.lock` snippet to appear to depend on `foo` but actually install `foo-2`
```
"foo 2.2.0" = [
  url = "https://files.pythonhosted.org/.../foo-2-2.tar.gz
]
```

### Impact
When installing dependencies with PDM, what's actually installed could differ from what's listed in `pyproject.toml` (including arbitrary code execution on install). It could also be used for downgrade attacks by only changing the version.

## References
- https://github.com/pdm-project/pdm/security/advisories/GHSA-j44v-mmf2-xvm9
- https://nvd.nist.gov/vuln/detail/CVE-2023-45805
- https://github.com/pdm-project/pdm/commit/6853e2642dfa281d4a9958fbc6c95b7e32d84831
- https://github.com/frostming/unearth/blob/eca170d9370ac5032f2e497ee9b1b63823d3fe0f/src/unearth/evaluator.py#L215-L229
- https://github.com/pdm-project/pdm
- https://github.com/pdm-project/pdm/blob/45d1dfa47d4900c14a31b9bb761e4c46eb5c9442/src/pdm/models/candidates.py#L98-L99
- https://peps.python.org/pep-0440/#post-release-spelling
