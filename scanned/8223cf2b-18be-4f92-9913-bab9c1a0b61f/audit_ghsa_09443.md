# [H] Jupyter Server has a  CORS Origin Validation Bypass via `re.match()` in `allow_origin_pat`

## Summary
Severity: High
Advisory: GHSA-24qx-w28j-9m6p
CVE: CVE-2026-40110
CWE: CWE-625, CWE-777
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:L/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-24qx-w28j-9m6p
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <2.18.0

## Details
Jupyter Server uses `re.match()` to validate the Origin header against the `allow_origin_pat` configuration.

Since `re.match()` only anchors at the start of the string, an attacker who controls a domain like `http://trusted.example.com.evil.com/` passes validation against a pattern intended to match only `trusted.example.com`.

### Impact

<=2.17.0

### Patches

057869a327c46730afede3eab0ca2d2e3e74acea, 49b34392feaa97735b3b777e3baf8f22f2a14ed8 

### Workarounds

Wrap your `allow_origin_pat` value with `^` and `$`

### References

https://github.com/jupyter-server/jupyter_server/pull/603
https://docs.python.org/3/library/re.html#re.fullmatch
https://docs.python.org/3/library/re.html#re.match

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-24qx-w28j-9m6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-40110
- https://github.com/jupyter-server/jupyter_server/pull/603
- https://github.com/jupyter-server/jupyter_server/commit/057869a327c46730afede3eab0ca2d2e3e74acea
- https://github.com/jupyter-server/jupyter_server/commit/49b34392feaa97735b3b777e3baf8f22f2a14ed8
- https://access.redhat.com/errata/RHSA-2026:43038
- https://access.redhat.com/security/cve/CVE-2026-40110
- https://bugzilla.redhat.com/show_bug.cgi?id=2466912
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2026-2187.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40110.json
