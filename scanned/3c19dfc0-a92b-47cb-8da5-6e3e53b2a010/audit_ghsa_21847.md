# [M] DNS Rebinding in etcd

## Summary
Severity: Medium
Advisory: GHSA-wf43-55jj-vwq8
CVE: CVE-2018-1099
CWE: CWE-20, CWE-350
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-wf43-55jj-vwq8
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd` — affected >=0 <3.4.0

## Details
DNS rebinding vulnerability found in etcd 3.3.1 and earlier. An attacker can control his DNS records to direct to localhost, and trick the browser into sending requests to localhost (or any other address).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1099
- https://github.com/coreos/etcd/issues/9353
- https://github.com/coreos/etcd/commit/a7e5790c82039945639798ae9a3289fe787f5e56
- https://bugzilla.redhat.com/show_bug.cgi?id=1552717
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JX7QTIT465BQGRGNCE74RATRQLKT2QE4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UPGYHMSKDPW5GAMI7BEP3XQRVRLLBJKS
