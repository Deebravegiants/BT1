# [M] Insertion of Sensitive Information into Log File in ansible

## Summary
Severity: Medium
Advisory: GHSA-8f4m-hccc-8qph
CVE: CVE-2021-20191
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-01
Source: https://github.com/advisories/GHSA-8f4m-hccc-8qph
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.18rc1
- PyPI: `ansible` — affected >=0 <2.8.19rc1
- PyPI: `ansible` — affected >=2.10.0a1 <2.10.7

## Details
A flaw was found in ansible. Credentials, such as secrets, are being disclosed in console log by default and not protected by no_log feature when using those modules. An attacker can take advantage of this information to steal those credentials. The highest threat from this vulnerability is to data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20191
- https://github.com/ansible/ansible/pull/73488
- https://github.com/ansible/ansible/pull/73489
- https://github.com/ansible/ansible/commit/cc82d986c40328d4ae81298a9d287c95a6326bb0
- https://github.com/ansible/ansible/commit/d74a1b1d1325af2a24848044cf2858987f5a3ecc
- https://access.redhat.com/security/cve/cve-2021-20191
- https://bugzilla.redhat.com/show_bug.cgi?id=1916813
- https://github.com/advisories/GHSA-8f4m-hccc-8qph
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2021-124.yaml
- https://lists.debian.org/debian-lts-announce/2023/12/msg00018.html
