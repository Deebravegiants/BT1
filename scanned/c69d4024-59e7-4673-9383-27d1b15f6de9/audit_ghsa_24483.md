# [H] librsvg DoS via Cyclic References

## Summary
Severity: High
Advisory: GHSA-j984-q4qc-6qxf
CVE: CVE-2015-7558
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j984-q4qc-6qxf
Type: github-advisory

## Affected
- crates.io: `librsvg` — affected >=0 <2.40.12

## Details
librsvg before 2.40.12 allows context-dependent attackers to cause a denial of service (infinite loop, stack consumption, and application crash) via cyclic references in an SVG document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7558
- https://bugzilla.redhat.com/show_bug.cgi?id=1268243
- https://git.gnome.org/browse/librsvg/commit/?id=a51919f7e1ca9c535390a746fbf6e28c8402dc61
- https://github.com/GNOME/librsvg
- http://www.debian.org/security/2016/dsa-3584
- http://www.openwall.com/lists/oss-security/2015/12/21/5
- http://www.openwall.com/lists/oss-security/2016/04/30/3
