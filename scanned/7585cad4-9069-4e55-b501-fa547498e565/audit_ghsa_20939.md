# [H] Blink1Control2 uses weak password encryption

## Summary
Severity: High
Advisory: GHSA-jqhq-pfg3-fg5p
CVE: CVE-2022-35513
CWE: CWE-326
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-08
Source: https://github.com/advisories/GHSA-jqhq-pfg3-fg5p
Type: github-advisory

## Affected
- npm: `Blink1Control2` — affected >=0 <2.2.9

## Details
The Blink1Control2 application <= 2.2.7 uses weak password encryption and an insecure method of storage. Version 2.2.9 fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35513
- https://github.com/todbot/Blink1Control2/issues/175
- https://github.com/todbot/Blink1Control2/commit/74827462aba3a26d7bf157522f69eec999d7ba85
- https://github.com/todbot/Blink1Control2/commit/cd9229ef9131bc663f714150c9f8d5cbf818d620
- https://github.com/todbot/Blink1Control2/commit/efe174823f67bbdcee8863e02df67a130f132075
- https://github.com/todbot/Blink1Control2/commit/f595d782d2356878188fed423a7dcb84ee8fee9d
- https://github.com/p1ckzi/CVE-2022-35513
- https://github.com/todbot/Blink1Control2
- https://github.com/todbot/Blink1Control2/releases
- http://packetstormsecurity.com/files/168428/Blink1Control2-2.2.7-Weak-Password-Encryption.html
