# [H] Matrix Synapse Predictable Secret Key

## Summary
Severity: High
Advisory: GHSA-jrqm-v8cv-53ww
CVE: CVE-2019-5885
CWE: CWE-330
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jrqm-v8cv-53ww
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <0.34.0.1

## Details
Matrix Synapse before 0.34.0.1, when the `macaroon_secret_key` authentication parameter is not set, uses a predictable value to derive a secret key and other secrets which could allow remote attackers to impersonate users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5885
- https://github.com/matrix-org/synapse/issues/4664
- https://github.com/matrix-org/synapse/pull/4315
- https://github.com/matrix-org/synapse/pull/4373
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/blob/67f9e5293ea6650b2ec284c0b7503f3f3eade94b/docs/changelogs/CHANGES-pre-1.0.md?plain=1#L460
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2019-187.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/32Y6KD3OAHCG5P33HC2QEX3NUZOSXCGZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VMCLO5PUPBA756UKY72PKUWL4RRM4W6K
- https://matrix.org/blog/2019/01/10/critical-security-update-synapse-0-34-0-1-synapse-0-34-1-1
- https://matrix.org/blog/2019/01/15/further-details-on-critical-security-update-in-synapse-affecting-all-versions-prior-to-0-34-1-cve-2019-5885
