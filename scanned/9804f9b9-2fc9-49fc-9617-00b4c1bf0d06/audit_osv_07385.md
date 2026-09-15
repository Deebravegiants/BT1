# [C] BIT-python-2007-4559

## Summary
Severity: Critical
Advisory: BIT-python-2007-4559
Aliases: BIT-python-min-2007-4559, CVE-2007-4559, PSF-2007-2
Ecosystem: Bitnami
Published: 2026-02-03
Source: https://osv.dev/vulnerability/BIT-python-2007-4559
Type: osv

## Affected
- Bitnami: `python` — affected >=3.11.0 <3.11.4

## Details
Directory traversal vulnerability in the (1) extract and (2) extractall functions in the tarfile module in Python allows user-assisted remote attackers to overwrite arbitrary files via a .. (dot dot) sequence in filenames in a TAR archive, a related issue to CVE-2001-1267.

## References
- http://mail.python.org/pipermail/python-dev/2007-August/074290.html
- http://mail.python.org/pipermail/python-dev/2007-August/074292.html
- http://secunia.com/advisories/26623
- http://www.vupen.com/english/advisories/2007/3022
- https://bugzilla.redhat.com/show_bug.cgi?id=263261
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CVBB7NU3YIRRDOKLYVN647WPRR3IAKR6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FI55PGL47ES3OU2FQPGEHOI2EK3S2OBH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KA4Z44ZAI4SY7THCFBUDNT5EEFO4XQ3A/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CVBB7NU3YIRRDOKLYVN647WPRR3IAKR6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FI55PGL47ES3OU2FQPGEHOI2EK3S2OBH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KA4Z44ZAI4SY7THCFBUDNT5EEFO4XQ3A/
- https://nvd.nist.gov/vuln/detail/CVE-2007-4559
- https://security.gentoo.org/glsa/202309-06
- https://github.com/advisories/GHSA-gw9q-c7gh-j9vm
