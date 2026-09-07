# [M] Graylog session fixation vulnerability through cookie injection

## Summary
Severity: Medium
Advisory: GHSA-3xf8-g8gr-g7rh
CVE: CVE-2024-24823
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-3xf8-g8gr-g7rh
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=4.3.0 <5.1.11
- Maven: `org.graylog2:graylog2-server` — affected >=5.2.0-alpha.1 <5.2.4

## Details
### Impact
Reauthenticating with an existing session cookie would re-use that session id, even if for different user credentials.
In this case, the pre-existing session could be used to gain elevated access to an existing Graylog login session, provided the malicious user could successfully inject their session cookie into someone else's browser.

The complexity of such an attack is high, because it requires presenting a spoofed login screen and injection of a session cookie into an existing browser, potentially through an XSS attack. No such attack has been discovered.

### Patches
Graylog 5.1.11 and 5.2.4, and any versions of the 6.0 development branch contain patches to not re-use sessions under any circumstances, making this type of attack impossible.

### Workarounds
Using short session expiration and explicit log outs of unused sessions can help limiting the attack vector. Unpatched this vulnerability exists, but is relatively hard to exploit.
A proxy could be leveraged to clear the `authentication` cookie for the Graylog server URL for the `/api/system/sessions` endpoint, as that is the only one vulnerable.

Analysis provided by Fabian Yamaguchi - Whirly Labs (Pty) Ltd

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-3xf8-g8gr-g7rh
- https://nvd.nist.gov/vuln/detail/CVE-2024-24823
- https://github.com/Graylog2/graylog2-server/commit/1596b749db86368ba476662f23a0f0c5ec2b5097
- https://github.com/Graylog2/graylog2-server/commit/b93a66353f35a94a4e8f3f75ac4f5cdc5a2d4a6a
- https://github.com/Graylog2/graylog2-server
