# [M] risesoft-y9 Digital-Infrastructure has a SQL injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vhcx-7rpg-hp39
CVE: CVE-2026-1050
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-01-17
Source: https://github.com/advisories/GHSA-vhcx-7rpg-hp39
Type: github-advisory

## Affected
- Maven: `net.risesoft:risenet-y9boot-support-platform-service` — affected >=0

## Details
A flaw has been found in risesoft-y9 Digital-Infrastructure up to 9.6.7. This affects an unknown function of the file source-code/src/main/java/net/risesoft/util/Y9PlatformUtil.java of the component REST Authenticate Endpoint. Executing a manipulation can lead to sql injection. The attack can be launched remotely. The exploit has been published and may be used. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1050
- https://github.com/risesoft-y9/Digital-Infrastructure/issues/2
- https://github.com/risesoft-y9/Digital-Infrastructure
- https://vuldb.com/?ctiid.341603
- https://vuldb.com/?id.341603
- https://vuldb.com/?submit.731010
