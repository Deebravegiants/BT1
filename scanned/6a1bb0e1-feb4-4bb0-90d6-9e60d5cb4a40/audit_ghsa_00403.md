# [H] Ansible apt_key module does not properly verify key fingerprint

## Summary
Severity: High
Advisory: GHSA-cmwx-9m2h-x7v4
CVE: CVE-2016-8614
CWE: CWE-358
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-cmwx-9m2h-x7v4
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.2.0.0

## Details
A flaw was found in Ansible before version 2.2.0.0. The `apt_key` module does not properly verify key fingerprints, allowing remote adversary to create an OpenPGP key which matches the short key ID and inject this key instead of the correct key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8614
- https://github.com/ansible/ansible-modules-core/issues/5237
- https://github.com/ansible/ansible-modules-core/pull/5353
- https://github.com/ansible/ansible-modules-core/pull/5357
- https://github.com/ansible/ansible-modules-core/commit/1182d1f0b76d56f3667e27987a10b9ec8f03357d
- https://github.com/ansible/ansible-modules-core/commit/66d47c8149d84e52f64b7c4d1f340d45dca94d9c
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8614
- https://github.com/advisories/GHSA-cmwx-9m2h-x7v4
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-37.yaml
- https://web.archive.org/web/20200227214450/https://www.securityfocus.com/bid/94108
