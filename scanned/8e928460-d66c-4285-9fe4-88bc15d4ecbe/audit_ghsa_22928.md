# [H] openstack-mistral Discloses the presence of arbitrary files within the filesystem

## Summary
Severity: High
Advisory: GHSA-fqw7-c6vr-q29m
CVE: CVE-2018-16849
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fqw7-c6vr-q29m
Type: github-advisory

## Affected
- PyPI: `mistral` — affected >=0 <7.0.1

## Details
A flaw was found in openstack-mistral. By manipulating the SSH private key filename, the std.ssh action can be used to disclose the presence of arbitrary files within the filesystem of the executor running the action. Since std.ssh private_key_filename can take an absolute path, it can be used to assess whether or not a file exists on the executor's filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16849
- https://github.com/openstack/mistral/commit/2309e5265a1d5f28480ae872817b5de05f66e83c
- https://github.com/openstack/mistral/commit/c93b45a61f49d4633f76d8e117cd89063e7759c4
- https://bugs.launchpad.net/mistral/+bug/1783708
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16849
- https://github.com/openstack/mistral
- https://github.com/pypa/advisory-database/tree/main/vulns/mistral/PYSEC-2018-92.yaml
