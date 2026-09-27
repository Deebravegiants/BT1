# [H] Cheetah Path Search Order Hijacking

## Summary
Severity: High
Advisory: GHSA-vxf2-7rc3-pxmx
CVE: CVE-2005-1632
CWE: CWE-427
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-vxf2-7rc3-pxmx
Type: github-advisory

## Affected
- PyPI: `cheetah` — affected >=0.9.15

## Details
Cheetah 0.9.15 and 0.9.16 searches the `/tmp` directory for modules before using the paths in the `PYTHONPATH` variable, which allows local users to execute arbitrary code via a malicious module in `/tmp/`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2005-1632
- https://github.com/cheetahtemplate/cheetah
- https://web.archive.org/web/20050430021153/http://sourceforge.net/mailarchive/forum.php?thread_id=7070332&forum_id=1542
