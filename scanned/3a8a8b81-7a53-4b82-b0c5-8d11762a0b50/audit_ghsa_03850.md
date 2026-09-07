# [H] High severity vulnerability that affects indico

## Summary
Severity: High
Advisory: GHSA-67cx-rhhq-mfhq
CWE: CWE-77
Ecosystem: PyPI
Published: 2019-10-11
Source: https://github.com/advisories/GHSA-67cx-rhhq-mfhq
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <2.1.10
- PyPI: `indico` — affected >=2.2.0 <2.2.3

## Details
## Local file disclosure through LaTeX injection

### Impact
An external audit of the Indico codebase has discovered a vulnerability in Indico's LaTeX sanitization code, which could have malicious users to run unsafe LaTeX commands on the server. Such commands allowed for example to read local files (e.g. `indico.conf`).

As far as we know it is not possible to write files or execute code using this vulnerability.

### Patches
You need to update to [Indico 2.2.3](https://github.com/indico/indico/releases/tag/v2.2.3) as soon as possible.
We also released [Indico 2.1.10](https://github.com/indico/indico/releases/tag/v2.1.10) in case you cannot update to 2.2 for some reason.
See https://docs.getindico.io/en/stable/installation/upgrade/ for instructions on how to update.

### Workarounds
Setting `XELATEX_PATH = None` in `indico.conf` will result in an error when building a PDF, but without being able to run xelatex, the vulnerability cannot be abused.

### For more information
If you have any questions or comments about this advisory:
* Open a thread in [our forum](https://talk.getindico.io/)
* Email us privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-67cx-rhhq-mfhq
- https://github.com/advisories/GHSA-67cx-rhhq-mfhq
- https://github.com/indico/indico
