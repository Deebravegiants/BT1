# [M] File System Bounds Escape

## Summary
Severity: Medium
Advisory: GHSA-pmw4-jgxx-pcq9
CVE: CVE-2020-26299
CWE: CWE-22
Ecosystem: npm
Published: 2021-02-10
Source: https://github.com/advisories/GHSA-pmw4-jgxx-pcq9
Type: github-advisory

## Affected
- npm: `ftp-srv` — affected >=0 <4.4.0

## Details
### Impact

Clients of FTP servers utilizing `ftp-srv` hosted on Windows machines can escape the  FTP user's defined root folder using the expected FTP commands, for example, `CWD` and `UPDR`.

### Background

When windows separators exist within the path (`\`), `path.resolve` leaves the upper pointers intact and allows the user to move beyond the root folder defined for that user. We did not take that into account when creating the path resolve function.

![Screen Shot 2020-12-15 at 6 42 52 PM](https://user-images.githubusercontent.com/3375444/102293941-5a75fb80-3f05-11eb-9d71-0c190a8dcc75.png)

### Patches
None at the moment.

### Workarounds
There are no workarounds for windows servers. Hosting the server on a different OS mitigates the issue.

### References

Issues: 
https://github.com/autovance/ftp-srv/issues/167
https://github.com/autovance/ftp-srv/issues/225

### For more information
If you have any questions or comments about this advisory:
Open an issue at https://github.com/autovance/ftp-srv.
Please email us directly; security@autovance.com.

## References
- https://github.com/autovance/ftp-srv/security/advisories/GHSA-pmw4-jgxx-pcq9
- https://nvd.nist.gov/vuln/detail/CVE-2020-26299
- https://github.com/autovance/ftp-srv/issues/167
- https://github.com/autovance/ftp-srv/issues/225
- https://github.com/autovance/ftp-srv/pull/224
- https://github.com/autovance/ftp-srv/commit/457b859450a37cba10ff3c431eb4aa67771122e3
- https://www.npmjs.com/package/ftp-srv
