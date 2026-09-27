# [H] Exposure of Sensitive Information to an Unauthorized Actor in ansible

## Summary
Severity: High
Advisory: GHSA-p75j-wc34-527c
CVE: CVE-2019-10217
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-p75j-wc34-527c
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.8.0a1 <2.8.4

## Details
A flaw was found in ansible 2.8.0 before 2.8.4. Fields managing sensitive data should be set as such by no_log feature. Some of these fields in GCP modules are not set properly. service_account_contents() which is common class for all gcp modules is not setting no_log to True. Any sensitive data managed by that function would be leak as an output when running ansible playbooks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10217
- https://github.com/ansible/ansible/issues/56269
- https://github.com/ansible/ansible/pull/59427
- https://github.com/ansible/ansible/commit/c1ee1f142db1e669b710a65147ea32be47a91519
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10217
- https://github.com/advisories/GHSA-p75j-wc34-527c
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2019-3.yaml
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00026.html
