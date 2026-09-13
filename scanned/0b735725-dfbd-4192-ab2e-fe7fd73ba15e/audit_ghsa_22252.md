# [M] Restkit Does Not Validate TLS certificates

## Summary
Severity: Medium
Advisory: GHSA-p9cv-hrxr-fxx8
CVE: CVE-2015-2674
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p9cv-hrxr-fxx8
Type: github-advisory

## Affected
- PyPI: `restkit` — affected >=0

## Details
Restkit allows man-in-the-middle attackers to spoof TLS servers by leveraging use of the `ssl.wrap_socket` function in Python with the default CERT_NONE value for the cert_reqs argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2674
- https://github.com/benoitc/restkit/issues/140
- https://bugzilla.redhat.com/show_bug.cgi?id=1202837
- https://github.com/benoitc/restkit
- https://github.com/pypa/advisory-database/tree/main/vulns/restkit/PYSEC-2017-69.yaml
- http://www.openwall.com/lists/oss-security/2015/03/23/7
