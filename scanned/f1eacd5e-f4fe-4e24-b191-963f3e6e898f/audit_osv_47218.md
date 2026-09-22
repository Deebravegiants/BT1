# [H] CVE-2016-1232

## Summary
Severity: High
Advisory: CVE-2016-1232
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-01-12
Source: https://osv.dev/vulnerability/CVE-2016-1232
Type: osv

## Details
The mod_dialback module in Prosody before 0.9.9 does not properly generate random values for the secret token for server-to-server dialback authentication, which makes it easier for attackers to spoof servers via a brute force attack.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175829.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175868.html
- http://www.openwall.com/lists/oss-security/2016/01/08/5
- https://prosody.im/issues/issue/571
- http://www.debian.org/security/2016/dsa-3439
- https://prosody.im/security/advisory_20160108-2/
- http://blog.prosody.im/prosody-0-9-9-security-release/
