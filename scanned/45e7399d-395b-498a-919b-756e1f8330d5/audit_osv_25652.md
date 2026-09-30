# [M] CVE-2023-4104

## Summary
Severity: Medium
Advisory: CVE-2023-4104
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-09-11
Source: https://osv.dev/vulnerability/CVE-2023-4104
Type: osv

## Details
An invalid Polkit Authentication check and missing authentication requirements for D-Bus methods allowed any local user to configure arbitrary VPN setups.
*This bug only affects Mozilla VPN on Linux. Other operating systems are unaffected.* This vulnerability affects Mozilla VPN 2.16.1 < (Linux).

## References
- https://www.openwall.com/lists/oss-security/2023/08/03/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4104.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4104
- https://www.mozilla.org/security/advisories/mfsa2023-39/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1831318
- https://github.com/mozilla-mobile/mozilla-vpn-client/pull/7055
- https://github.com/mozilla-mobile/mozilla-vpn-client/pull/7110
- https://github.com/mozilla-mobile/mozilla-vpn-client/pull/7151
