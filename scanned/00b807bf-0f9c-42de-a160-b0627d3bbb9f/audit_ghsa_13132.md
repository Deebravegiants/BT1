# [M] Cros secrets may be disclosed to untrusted relay

## Summary
Severity: Medium
Advisory: GHSA-hp56-xvf4-g6wr
CVE: CVE-2023-43617
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-hp56-xvf4-g6wr
Type: github-advisory

## Affected
- Go: `github.com/schollz/croc/v9` — affected >=0 <9.6.16

## Details
An issue was discovered in Croc before 9.6.16. When a custom shared secret is used, the sender and receiver may divulge parts of this secret to an untrusted Relay, as part of composing a room name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43617
- https://github.com/schollz/croc/issues/596
- https://github.com/schollz/croc/pull/699
- https://github.com/schollz/croc/commit/0f1ca436cd8e608738da0b23bf594537cfbe6213
- https://github.com/schollz/croc
- https://www.openwall.com/lists/oss-security/2023/09/08/2
- http://www.openwall.com/lists/oss-security/2023/09/21/5
