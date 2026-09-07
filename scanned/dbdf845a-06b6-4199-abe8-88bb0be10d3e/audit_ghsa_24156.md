# [M] Insecure Temporary File in Jinja2

## Summary
Severity: Medium
Advisory: GHSA-fqh9-2qgg-h84h
CVE: CVE-2014-0012
CWE: CWE-377
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fqh9-2qgg-h84h
Type: github-advisory

## Affected
- PyPI: `Jinja2` — affected >=0 <2.7.2

## Details
FileSystemBytecodeCache in Jinja2 prior to version 2.7.2 does not properly create temporary directories, which allows local users to gain privileges by pre-creating a temporary directory with a user's uid. NOTE: this vulnerability exists because of an incomplete fix for CVE-2014-1402.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0012
- https://github.com/mitsuhiko/jinja2/pull/292
- https://github.com/mitsuhiko/jinja2/pull/296
- https://github.com/pallets/jinja2/pull/292
- https://github.com/pallets/jinja2/pull/296
- https://github.com/mitsuhiko/jinja2/commit/acb672b6a179567632e032f547582f30fa2f4aa7
- https://github.com/pallets/jinja/commit/acb672b6a179567632e032f547582f30fa2f4aa7
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=734747
- https://bugzilla.redhat.com/show_bug.cgi?id=1051421
- https://github.com/pallets/jinja2
- https://github.com/pypa/advisory-database/tree/main/vulns/jinja2/PYSEC-2014-82.yaml
- http://seclists.org/oss-sec/2014/q1/73
- http://www.gentoo.org/security/en/glsa/glsa-201408-13.xml
