# [M] Archive spoofing vulnerability in borgbackup

## Summary
Severity: Medium
Advisory: GHSA-8fjr-hghr-4m99
CVE: CVE-2023-36811
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-08-30
Source: https://github.com/advisories/GHSA-8fjr-hghr-4m99
Type: github-advisory

## Affected
- PyPI: `borgbackup` — affected >=0 <1.2.5

## Details
### Impact
A flaw in the cryptographic authentication scheme in borgbackup allowed an attacker to fake archives and potentially indirectly cause backup data loss in the repository.

The attack requires an attacker to be able to

1. insert files (with no additional headers) into backups
2. gain write access to the repository

This vulnerability does not disclose plaintext to the attacker, nor does it affect the authenticity of existing archives.

Creating plausible fake archives may be feasible for empty or small archives, but is unlikely for large archives.

Affected are all borgbackup releases prior to 1.2.5.

Note: CVSS scoring model seemed to badly fit for this case, thus I manually set score to "moderate".

### Patches
The issue has been fixed in borgbackup 1.2.5.
But there was a bug in 1.2.5 upgrade instructions, thus 1.2.6 with an important fix in docs and code was released a day afterwards.

Additionally to installing the fixed code, users must follow the upgrade procedure as documented in the latest version of the change log.

### Workarounds
Data loss after being attacked can be avoided by reviewing the archives (timestamp and contents valid and as expected) after any "borg check --repair" and before "borg prune".

### References

https://github.com/borgbackup/borg/blob/1.2.6/docs/changes.rst#pre-125-archives-spoofing-vulnerability-cve-2023-36811

## References
- https://github.com/borgbackup/borg/security/advisories/GHSA-8fjr-hghr-4m99
- https://nvd.nist.gov/vuln/detail/CVE-2023-36811
- https://github.com/borgbackup/borg/commit/3eb070191da10c2d3f7bc6484cf3d51c3045f884
- https://github.com/borgbackup/borg
- https://github.com/borgbackup/borg/blob/1.2.5-cvedocs/docs/changes.rst#pre-125-archives-spoofing-vulnerability-cve-2023-36811
- https://github.com/borgbackup/borg/blob/1.2.6/docs/changes.rst#pre-125-archives-spoofing-vulnerability-cve-2023-36811
- https://github.com/pypa/advisory-database/tree/main/vulns/borgbackup/PYSEC-2023-164.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5Q3OHXERTU547SEQ3YREZXHOCYNLVD63
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XOZDFIYEBIOKSIEAXUJJJFUJTAJ7TF3C
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZUCQSMAWOJBCRGF6XPKEZ2TPGAPNKIWV
