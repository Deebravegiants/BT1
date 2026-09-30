# [H] OS Command Injection in ansible

## Summary
Severity: High
Advisory: GHSA-h39q-95q5-9jfp
CVE: CVE-2020-1734
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-h39q-95q5-9jfp
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.10.0a1 <2.10.0rc1
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.11
- PyPI: `ansible` — affected >=0 <2.8.13

## Details
A flaw was found in the pipe lookup plugin of ansible. Arbitrary commands can be run, when the pipe lookup plugin uses `subprocess.Popen()` with `shell=True`, by overwriting ansible facts and the variable is not escaped by quote plugin. An attacker could take advantage and run arbitrary commands by overwriting the ansible facts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1734
- https://github.com/ansible/ansible/issues/67792
- https://github.com/ansible/ansible/issues/70159
- https://github.com/ansible/ansible/pull/70596
- https://github.com/ansible/ansible/commit/4f978af4ca16ad9828ffe42203b9615425195f8b
- https://github.com/ansible/ansible/commit/963bdd9983b91a48fb6949fb2ef41071e72d0be0
- https://github.com/ansible/ansible/commit/bff0724e9eab2770f874e018298f9ab74cc2a78f
- https://github.com/ansible/ansible/commit/e5649ca3e807f17e7c034ee22791f107162973b0
- https://access.redhat.com/errata/RHBA-2020:0547
- https://access.redhat.com/errata/RHBA-2020:1539
- https://access.redhat.com/security/cve/CVE-2020-1734
- https://bugzilla.redhat.com/show_bug.cgi?id=1801804
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1734
- https://github.com/advisories/GHSA-h39q-95q5-9jfp
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-6.yaml
