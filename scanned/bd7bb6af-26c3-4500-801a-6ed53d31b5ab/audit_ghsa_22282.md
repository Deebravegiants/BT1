# [H] Tornado XSRF cookie allows side-channel attack against TLS (BREACH attack)

## Summary
Severity: High
Advisory: GHSA-8vpw-mgpf-mpvv
CVE: CVE-2014-9720
CWE: CWE-203
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8vpw-mgpf-mpvv
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <3.2.2

## Details
Tornado before 3.2.2 sends arbitrary responses that contain a fixed CSRF token and may be sent with HTTP compression, which makes it easier for remote attackers to conduct a BREACH attack and determine this token via a series of crafted requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9720
- https://github.com/tornadoweb/tornado/commit/1c36307463b1e8affae100bf9386948e6c1b2308
- https://bugzilla.novell.com/show_bug.cgi?id=930362
- https://bugzilla.redhat.com/show_bug.cgi?id=1222816
- https://github.com/pypa/advisory-database/tree/main/vulns/tornado/PYSEC-2020-213.yaml
- https://github.com/tornadoweb/tornado
- http://openwall.com/lists/oss-security/2015/05/19/4
- http://www.tornadoweb.org/en/stable/releases/v3.2.2.html
