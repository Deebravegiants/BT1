# [H] Arbitrary command execution on Windows via qutebrowserurl: URL handler

## Summary
Severity: High
Advisory: GHSA-vw27-fwjf-5qxm
CVE: CVE-2021-41146
CWE: CWE-641, CWE-77, CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-22
Source: https://github.com/advisories/GHSA-vw27-fwjf-5qxm
Type: github-advisory

## Affected
- PyPI: `qutebrowser` — affected >=1.7.0 <2.4.0

## Details
### Impact
Starting with qutebrowser v1.7.0, the Windows installer for qutebrowser registers it as a handler for certain URL schemes. With some applications such as Outlook Desktop, opening a specially crafted URL can lead to argument injection, allowing execution of qutebrowser commands, which in turn allows arbitrary code execution via commands such as `:spawn` or `:debug-pyeval`.

Only Windows installs where qutebrowser is registered as URL handler are affected. It does *not* have to be set as default browser for the exploit to work.

### Patches
The issue has been fixed in [qutebrowser v2.4.0](https://github.com/qutebrowser/qutebrowser/releases/tag/v2.4.0) in commit 8f46ba3f6dc7b18375f7aa63c48a1fe461190430.

The fix also adds additional hardening for potential similar issues on Linux (by adding the new `--untrusted-args` flag to the `.desktop` file), though no such vulnerabilities are known.

Backported patches for older versions are available, but no further releases are planned:

- v1.7.x: d1ceaab
- v1.8.x: ca7155d
- v1.9.x: 157d871
- v1.10.x: 94a6125
- v1.11.x: 10acfbb
- v1.12.x: 363a18f
- v1.13.x: 410f262
- v1.14.x: e4f4d93
- v2.0.x: 15a1654
- v2.1.x: 509ddf2
- v2.2.x: 03dcba5
- v2.3.x: 00a694c

(commits are referring to qutebrowser/qutebrowser on GitHub)

### Workarounds
Remove qutebrowser from the default browser settings entirely, so that it does not handle any kind of URLs. Make sure to remove *all* handlers, including an (accidental) `qutebrowserURL` handler, e.g. using [NirSoft URLProtocolView](https://www.nirsoft.net/utils/url_protocol_view.html).

### Timeline
2021-10-15: Issue reported via security@qutebrowser.org by Ping Fan (Zetta) Ke of [Valkyrie-X Security Research Group (VXRL)](https://www.vxrl.hk/)
2021-10-15: Issue confirmed by @The-Compiler (lead developer), author of installer (@bitraid) contacted for help/review
2021-10-15: CVE assigned by GitHub
2021-10-15 to 2021-10-17: Fix developed
2021-10-17: Additional core developer (@toofar) contacted for help/review
2021-10-21: v2.4.0 released containing the fix
2021-10-21: Advisory and fix published

### References
See the [commit message](https://github.com/qutebrowser/qutebrowser/commit/8f46ba3f6dc7b18375f7aa63c48a1fe461190430) for additional information and references to various similar issues in other projects.

### Acknowledgements
Thanks to Ping Fan (Zetta) Ke of [Valkyrie-X Security Research Group](https://www.vxrl.hk/) (VXRL/@vxresearch) for finding and responsibly disclosing this issue.

### Contact
If you have any questions or comments about this advisory, please email [security@qutebrowser.org](mailto:security@qutebrowser.org).

## References
- https://github.com/qutebrowser/qutebrowser/security/advisories/GHSA-vw27-fwjf-5qxm
- https://nvd.nist.gov/vuln/detail/CVE-2021-41146
- https://github.com/qutebrowser/qutebrowser/commit/8f46ba3f6dc7b18375f7aa63c48a1fe461190430
- https://github.com/pypa/advisory-database/tree/main/vulns/qutebrowser/PYSEC-2021-382.yaml
- https://github.com/qutebrowser/qutebrowser
