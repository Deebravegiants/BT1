# [H] Potential Command Injection in codem-transcode

## Summary
Severity: High
Advisory: GHSA-rph7-j9qr-h8q8
CVE: CVE-2013-7377
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-11-28
Source: https://github.com/advisories/GHSA-rph7-j9qr-h8q8
Type: github-advisory

## Affected
- npm: `codem-transcode` — affected >=0 <0.5.0

## Details
When the ffprobe functionality is enabled on the server, HTTP POST requests can be made to /probe. These requests are passed to the ffprobe binary on the server. Through this HTTP endpoint it is possible to send a malformed source file name to ffprobe that results in arbitrary command execution.

### Mitigating Factors:
The ffprobe functionality is not enabled by default. In addition, exploitation opportunities are limited in a standard configuration because the server binds to the local interface by default.


## Recommendation

An updated and patched version of the module (version 0.5.0) is available via npm. Users who have enabled the ffprobe functionality are especially encouraged to upgrade..

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7377
- https://github.com/advisories/GHSA-rph7-j9qr-h8q8
- https://www.npmjs.com/advisories/2
- http://www.openwall.com/lists/oss-security/2014/05/13/1
- http://www.openwall.com/lists/oss-security/2014/05/15/2
