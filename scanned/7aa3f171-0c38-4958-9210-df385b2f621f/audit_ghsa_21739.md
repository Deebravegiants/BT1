# [M] Improper Validation of Certificate with Host Mismatch in mellium.im/xmpp/websocket

## Summary
Severity: Medium
Advisory: GHSA-h289-x5wc-xcv8
CVE: CVE-2022-24968
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-h289-x5wc-xcv8
Type: github-advisory

## Affected
- Go: `mellium.im/xmpp` — affected >=0.18.0 <0.21.1

## Details
### Impact

If no TLS configuration is provided by the user, the websocket package constructs its own TLS configuration using recommended defaults. When looking up a WSS endpoint using the DNS TXT record method described in [XEP-0156: Discovering Alternative XMPP Connection Methods](https://xmpp.org/extensions/xep-0156.html) the ServerName field was incorrectly being set to the name of the server returned by the TXT record request, not the name of the initial server we were attempting to connect to. This means that any attacker that can spoof a DNS record (ie. in the absence of DNSSEC, DNS-over-TLS, DNS-over-HTTPS, or similar technologies) could redirect the user to a server of their choosing and as long as it had a valid TLS certificate for itself the connection would succeed, resulting in a MITM situation.

### Patches

All users should upgrade to v0.21.1.

### Workarounds

To work around the issue, manually specify a TLS configuration with the correct hostname.

### References

- https://mellium.im/cve/cve-2022-24968/
- https://nvd.nist.gov/vuln/detail/CVE-2022-24968

### For more information

If you have any questions or comments about this advisory:
* Reach out on XMPP to [sam@samwhited.com](xmpp:sam@samwhited.com?msg)
* Email us at [sam@samwhited.com](mailto:sam@samwhited.com)

## References
- https://github.com/mellium/xmpp/security/advisories/GHSA-h289-x5wc-xcv8
- https://nvd.nist.gov/vuln/detail/CVE-2022-24968
- https://github.com/mellium/xmpp/pull/260
- https://github.com/mellium/xmpp/commit/0d92aa486da69b71f2f4a30e62aa722c711b98ac
- https://github.com/mellium/xmpp
- https://mellium.im/cve/cve-2022-24968
- https://mellium.im/issue/259
- https://pkg.go.dev/vuln/GO-2022-0370
