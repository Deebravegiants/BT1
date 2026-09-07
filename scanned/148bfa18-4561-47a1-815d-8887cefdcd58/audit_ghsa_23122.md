# [H] Grafana world readable configuration files

## Summary
Severity: High
Advisory: GHSA-m25m-5778-fm22
CVE: CVE-2020-12459
CWE: CWE-200, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m25m-5778-fm22
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=6.0.0-beta1 <7.2.1

## Details
In certain Red Hat packages for Grafana 6.x through 6.3.6, the configuration files `/etc/grafana/grafana.ini` and `/etc/grafana/ldap.toml` (which contain a secret_key and a bind_password) are world readable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12459
- https://github.com/grafana/grafana/issues/8283
- https://github.com/grafana/grafana/commit/102448040d5132460e3b0013e03ebedec0677e00
- https://access.redhat.com/security/cve/CVE-2020-12459
- https://bugzilla.redhat.com/show_bug.cgi?id=1827765
- https://bugzilla.redhat.com/show_bug.cgi?id=1829724
- https://github.com/grafana/grafana
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CTQCKJZZYXMCSHJFZZ3YXEO5NUBANGZS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WEBCIEVSYIDDCA7FTRS2IFUOYLIQU34A
- https://security.netapp.com/advisory/ntap-20200518-0004
- https://src.fedoraproject.org/rpms/grafana/c/fab93d67363eb0a9678d9faf160cc88237f26277
