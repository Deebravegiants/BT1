# [M] Token bruteforcing.

## Summary
Severity: Medium
Advisory: GHSA-v7vq-3x77-87vg
CVE: CVE-2022-29238
CWE: CWE-425
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-v7vq-3x77-87vg
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <6.4.12

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Authenticated requests to the notebook server with `ContentsManager.allow_hidden = False` only prevented listing the contents of hidden directories, not accessing individual hidden files or files in hidden directories (i.e. hidden files were 'hidden' but not 'inaccessible'). This could lead to notebook configurations allowing authenticated access to files that may reasonably be expected to be disallowed.

Because fully authenticated requests are required, this is of relatively low impact. But if a server's root directory contains sensitive files whose only protection from the server is being hidden (e.g. `~/.ssh` while serving $HOME), then any authenticated requests could access files if their names are guessable. Such contexts also necessarily have full access to the server and therefore execution permissions, which also generally grants access to all the same files. So this does not generally result in any privilege escalation or increase in information access, only an additional, unintended _means_ by which the files could be accessed.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

notebook 6.4.12

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

- Do not run the notebook server in a directory with hidden files, use subdirectories
- Use a custom ContentsManager with additional checks for `self.is_hidden(path)` prior to completing actions

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [example link to repo](http://example.com)
* Email us at [example email address](mailto:example@example.com)

## References
- https://github.com/jupyter/notebook/security/advisories/GHSA-v7vq-3x77-87vg
- https://nvd.nist.gov/vuln/detail/CVE-2022-29238
- https://github.com/jupyter/notebook
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2022-212.yaml
