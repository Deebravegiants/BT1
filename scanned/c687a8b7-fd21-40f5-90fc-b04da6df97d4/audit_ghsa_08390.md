# [M] Nautobot: Object bulk rename UI actions vulnerable to denial of service by crafted regular expression (REDoS)

## Summary
Severity: Medium
Advisory: GHSA-qrpw-gjvh-x5gm
CVE: CVE-2026-44796
CWE: CWE-1333, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-qrpw-gjvh-x5gm
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=3.0.0a2 <3.1.2
- PyPI: `nautobot` — affected >=0 <2.4.33

## Details
### Impact

Nautobot UI object-bulk-rename endpoints (for example, `/dcim/interfaces/rename/`) were vulnerable to application-wide denial of service via maliciously crafted regular expressions in the `find` field in combination with the `use_regex` flag.

### Patches

A general-purpose timeout has been added to these endpoints in Nautobot v2.4.33 and v3.1.2, which ensures that the request will fail early with an appropriate message if regular expression evaluation takes more than a short period of time, instead of continuing to execute for an indefinite duration.

### Workarounds

No known workaround has been identified at this time.

### References

- 2.4.33 (<a href="https://github.com/nautobot/nautobot/commit/c2b766966d814a7141f62c7bc90c85fefb7892ee">patch</a>)
- 3.1.2 (<a href="https://github.com/nautobot/nautobot/commit/5a30d0916953afbeedd24a784709e762cc3879cd">patch</a>)

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-qrpw-gjvh-x5gm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44796
- https://github.com/nautobot/nautobot/commit/5a30d0916953afbeedd24a784709e762cc3879cd
- https://github.com/nautobot/nautobot/commit/c2b766966d814a7141f62c7bc90c85fefb7892ee
- https://github.com/nautobot/nautobot
- https://github.com/nautobot/nautobot/releases/tag/v2.4.33
- https://github.com/nautobot/nautobot/releases/tag/v3.1.2
