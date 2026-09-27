# [H] Incorrect Privilege Assignment in Jinja2

## Summary
Severity: High
Advisory: GHSA-8r7q-cvjq-x353
CVE: CVE-2014-1402
CWE: CWE-266
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8r7q-cvjq-x353
Type: github-advisory

## Affected
- PyPI: `Jinja2` — affected >=0 <2.7.2

## Details
The default configuration for `bccache.FileSystemBytecodeCache` in Jinja2 before 2.7.2 does not properly create temporary files, which allows local users to gain privileges via a crafted .cache file with a name starting with `__jinja2_` in `/tmp`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1402
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=734747
- https://bugzilla.redhat.com/show_bug.cgi?id=1051421
- https://github.com/advisories/GHSA-8r7q-cvjq-x353
- https://github.com/pypa/advisory-database/tree/main/vulns/jinja2/PYSEC-2014-8.yaml
- https://oss.oracle.com/pipermail/el-errata/2014-June/004192.html
- https://web.archive.org/web/20150523060528/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2014:096/?name=MDVSA-2014:096
- http://advisories.mageia.org/MGASA-2014-0028.html
- http://jinja.pocoo.org/docs/changelog
- http://openwall.com/lists/oss-security/2014/01/10/2
- http://openwall.com/lists/oss-security/2014/01/10/3
- http://rhn.redhat.com/errata/RHSA-2014-0747.html
- http://rhn.redhat.com/errata/RHSA-2014-0748.html
- http://www.gentoo.org/security/en/glsa/glsa-201408-13.xml
