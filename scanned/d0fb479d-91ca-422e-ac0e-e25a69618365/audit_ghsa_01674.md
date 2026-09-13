# [M] HTTP Smuggling via Transfer-Encoding Header in Puma

## Summary
Severity: Medium
Advisory: GHSA-w64w-qqph-5gxm
CVE: CVE-2020-11077
CWE: CWE-444
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-05-22
Source: https://github.com/advisories/GHSA-w64w-qqph-5gxm
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=0 <3.12.6
- RubyGems: `puma` — affected >=4.0.0 <4.3.5

## Details
### Impact
This is a similar but different vulnerability to the one patched in 3.12.5 and 4.3.4.

A client could smuggle a request through a proxy, causing the proxy to send a response back to another unknown client. 

If the proxy uses persistent connections and the client adds another request in via HTTP pipelining, the proxy may mistake it as the first request's body. Puma, however, would see it as two requests, and when processing the second request, send back a response that the proxy does not expect. If the proxy has reused the persistent connection to Puma to send another request for a different client, the second response from the first client will be sent to the second client.

### Patches

The problem has been fixed in Puma 3.12.6 and Puma 4.3.5.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [Puma](https://github.com/puma/puma)
* See our [security policy](https://github.com/puma/puma/security/policy)

## References
- https://github.com/puma/puma/security/advisories/GHSA-w64w-qqph-5gxm
- https://nvd.nist.gov/vuln/detail/CVE-2020-11077
- https://github.com/puma/puma
- https://github.com/puma/puma/blob/master/History.md#434435-and-31253126--2020-05-22
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2020-11077.yml
- https://lists.debian.org/debian-lts-announce/2020/10/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SKIY5H67GJIGJL6SMFWFLUQQQR3EMVPR
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00038.html
