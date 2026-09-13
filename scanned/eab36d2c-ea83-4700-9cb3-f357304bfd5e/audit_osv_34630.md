# [M] ClipBucket v5 is vulnerable to password reset link manipulation

## Summary
Severity: Medium
Advisory: CVE-2025-62709
Aliases: GHSA-xhhf-mpqr-2cq5
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-11-20
Source: https://osv.dev/vulnerability/CVE-2025-62709
Type: osv

## Details
ClipBucket v5 is an open source video sharing platform. In ClipBucket version 5.5.2, a change to network.class.php causes the application to dynamically build the server URL from the incoming HTTP Host header when the configuration base_url is not set. Because Host is a client-controlled header, an attacker can supply an arbitrary Host value. This allows an attacker to cause password-reset links (sent by forget.php) to be generated with the attacker’s domain. If a victim follows that link and enters their activation code on the attacker-controlled domain, the attacker can capture the code and use it to reset the victim’s password and take over the account. This issue has been patched in version 5.5.2#162.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62709.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-xhhf-mpqr-2cq5
- https://nvd.nist.gov/vuln/detail/CVE-2025-62709
- https://github.com/MacWarrior/clipbucket-v5/commit/1a93532e665217b5d329808ca78e37e59e9f8a9d
