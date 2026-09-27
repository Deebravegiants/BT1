# [M] coreDNS vulnerable to Improper Restriction of Communication Channel to Intended Endpoints

## Summary
Severity: Medium
Advisory: GHSA-ch7v-37xg-75ph
CVE: CVE-2022-2835
CWE: CWE-923
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-ch7v-37xg-75ph
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0

## Details
A flaw was found in coreDNS. This flaw allows a malicious user to reroute internal calls to some internal services that were accessed by the FQDN in a format of <service>.<namespace>.svc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2835
- https://bugzilla.redhat.com/show_bug.cgi?id=2118542
- https://github.com/coredns/coredns
