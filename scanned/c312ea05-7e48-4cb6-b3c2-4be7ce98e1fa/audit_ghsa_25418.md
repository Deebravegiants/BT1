# [H] Django Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-qc99-g3wm-hgxr
CVE: CVE-2007-0404
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-qc99-g3wm-hgxr
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0.95 <1.0

## Details
`bin/compile-messages.py` in Django 0.95 does not quote argument strings before invoking the msgfmt program through the os.system function, which allows attackers to execute arbitrary commands via shell metacharacters in a (1) .po or (2) .mo file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-0404
- https://github.com/django/django/commit/518d406e53
- https://github.com/django/django/commit/a132d411c6986418ee6c0edc331080aa792fee6e
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=407519
- https://exchange.xforce.ibmcloud.com/vulnerabilities/31627
- https://github.com/django/django
- http://code.djangoproject.com/changeset/3592
