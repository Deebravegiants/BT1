# [H] DNSJava affected by KeyTrap - NSEC3 closest encloser proof can exhaust CPU resources

## Summary
Severity: High
Advisory: GHSA-mmwx-rj87-vfgr
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-mmwx-rj87-vfgr
Type: github-advisory

## Affected
- Maven: `dnsjava:dnsjava` — affected >=3.5.0 <3.6.0
- Maven: `org.jitsi:dnssecjava` — affected >=0

## Details
### Impact
Users using the `ValidatingResolver` for DNSSEC validation can run into CPU exhaustion with specially crafted DNSSEC-signed zones.

### Patches
Users should upgrade to dnsjava v3.6.0

### Workarounds
Although not recommended, only using a non-validating resolver, will remove the vulnerability.

### References
https://www.athene-center.de/en/keytrap

## References
- https://github.com/dnsjava/dnsjava/security/advisories/GHSA-mmwx-rj87-vfgr
- https://nvd.nist.gov/vuln/detail/CVE-2023-50868
- https://github.com/dnsjava/dnsjava/commit/711af79be3214f52daa5c846b95766dc0a075116
- https://github.com/advisories/GHSA-pv4h-p8jr-6cv2
- https://github.com/dnsjava/dnsjava
