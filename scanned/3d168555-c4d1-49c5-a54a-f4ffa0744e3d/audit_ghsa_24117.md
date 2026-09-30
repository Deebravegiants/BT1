# [H] ovirt-engine-sdk-python improper validation of hostname in x.509 certificate

## Summary
Severity: High
Advisory: GHSA-wf9j-m9fv-92gq
CVE: CVE-2014-0161
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wf9j-m9fv-92gq
Type: github-advisory

## Affected
- PyPI: `ovirt-engine-sdk-python` — affected >=0 <3.4.0.7
- PyPI: `ovirt-engine-sdk-python` — affected >=3.5.0.0 <3.5.0.4

## Details
ovirt-engine-sdk-python before 3.4.0.7 and 3.5.0.4 does not verify that the hostname of the remote endpoint matches the Common Name (CN) or subjectAltName as specified by its x.509 certificate in a TLS/SSL session. This could allow man-in-the-middle attackers to spoof remote endpoints via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0161
- https://access.redhat.com/security/cve/cve-2014-0161
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2014-0161
- https://github.com/oVirt/python-ovirt-engine-sdk4
- https://github.com/pypa/advisory-database/tree/main/vulns/ovirt-engine-sdk-python/PYSEC-2020-245.yaml
