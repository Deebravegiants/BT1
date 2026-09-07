# [H] etcd Cross-site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-5gjm-fj42-x983
CVE: CVE-2018-1098
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-5gjm-fj42-x983
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/v3` — affected >=0 <3.4.0

## Details
A cross-site request forgery flaw was found in etcd 3.3.1 and earlier. An attacker can set up a website that tries to send a POST request to the etcd server and modify a key. Adding a key is done with PUT so it is theoretically safe (can't PUT from an HTML form or such) but POST allows creating in-order keys that an attacker can send.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1098
- https://github.com/coreos/etcd/issues/9353
- https://github.com/coreos/etcd/commit/a7e5790c82039945639798ae9a3289fe787f5e56
- https://bugzilla.redhat.com/show_bug.cgi?id=1552714
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JX7QTIT465BQGRGNCE74RATRQLKT2QE4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPGYHMSKDPW5GAMI7BEP3XQRVRLLBJKS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JX7QTIT465BQGRGNCE74RATRQLKT2QE4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UPGYHMSKDPW5GAMI7BEP3XQRVRLLBJKS
