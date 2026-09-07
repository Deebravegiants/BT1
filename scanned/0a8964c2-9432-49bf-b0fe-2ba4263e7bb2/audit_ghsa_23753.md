# [H] rtslib-fb weak permissions for /etc/target/saveconfig.json file

## Summary
Severity: High
Advisory: GHSA-cpcw-p965-wpqx
CVE: CVE-2020-14019
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cpcw-p965-wpqx
Type: github-advisory

## Affected
- PyPI: `rtslib-fb` — affected >=0 <2.1.73

## Details
Python rtslib-fb through 2.1.72 has weak permissions for `/etc/target/saveconfig.json` because shutil.copyfile (instead of shutil.copy) is used, and thus permissions are not preserved.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14019
- https://github.com/open-iscsi/rtslib-fb/pull/162
- https://github.com/open-iscsi/rtslib-fb/commit/b23d061ee0fa7924d2cdce6194c313b9ee06c468
- https://github.com/open-iscsi/rtslib-fb
- https://github.com/pypa/advisory-database/tree/main/vulns/rtslib-fb/PYSEC-2020-250.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TNMCV2DJJTX345YYBXAMJBXNNVUZQ5UH
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00012.html
