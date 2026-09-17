# [H] Indico discloses local files resulting in Remote Code Execution through LaTeX injection 

## Summary
Severity: High
Advisory: GHSA-rm2q-f7jv-3cfp
CVE: CVE-2026-33046
CWE: CWE-22, CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-rm2q-f7jv-3cfp
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <3.3.12

## Details
> [!NOTE]
> If server-side LaTeX rendering is not in use (ie `XELATEX_PATH` was not set in `indico.conf`), this vulnerability does not apply.

### Impact
Due to vulnerabilities in TeXLive and obscure LaTeX syntax that allowed circumventing Indico's LaTeX sanitizer, it is possible to use specially-crafted LaTeX snippets which can read local files or execute code with the privileges of the user running Indico on the server.

### Patches
It is recommended to update to [Indico 3.3.12](https://github.com/indico/indico/releases/tag/v3.3.12) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

It is also strongly recommended to enable the containerized LaTeX renderer (using `podman`), which isolates it from the rest of the system. See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/#upgrading-to-3-3-12) for details - it is very easy and from now on the only recommended/supported way of using LaTeX.

### Workarounds
Remove the `XELATEX_PATH` setting from `indico.conf` (or comment it out or set it to `None`) and restart the `indico-uwsgi` and `indico-celery` services to disable LaTeX functionality.

### For more information
For any questions or comments about this advisory:

- Open a thread in [the forum](https://talk.getindico.io/)
- Send an email to [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-rm2q-f7jv-3cfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33046
- https://github.com/indico/indico/commit/0adb70f0ed66e129361d447868f5f3eb90dc5e96
- https://github.com/indico/indico/commit/1dbb12525b3de14229bf4d1ae192988068f975f6
- https://github.com/indico/indico/commit/5f24d23ce9c4b0e4b68b3d0b58987a948fc57c8a
- https://github.com/indico/indico/commit/fb169ced710c30cf792ce4b9f48688db0633cfd8
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.3.12
