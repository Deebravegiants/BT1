# [H] NeuVector OpenID Connect is vulnerable to man-in-the-middle (MITM)

## Summary
Severity: High
Advisory: GHSA-4jj9-cgqc-x9h5
CVE: CVE-2025-66001
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-4jj9-cgqc-x9h5
Type: github-advisory

## Affected
- Go: `github.com/neuvector/neuvector` — affected >=5.3.0 <5.4.8

## Details
### Impact

NeuVector supports login authentication through OpenID Connect. However, the TLS verification (which verifies the remote server's authenticity and integrity) for OpenID Connect is not enforced by default. As a result this may expose the system to man-in-the-middle (MITM) attacks.
Starting from version 5.4.0, NeuVector supports TLS verification for following connection types:

- Registry Connections
- Auth Server Connections (SAML, LDAP and OIDC)
- Webhook Connections

By default, TLS verification remains disabled, and its configuration is located under **Settings > Configuration in the NeuVector UI**.

In the patched version, the new NeuVector deployment enables TLS verification by default. 
For rolling upgrades, NeuVector does not automatically change this setting to prevent disruptions.

**Note:** When "TLS verification" is enabled, it affects all connections to:

- Registry servers
- Auth servers (SAML, LDAP and OIDC)
- Webhook servers

### Patches

Patched versions include release v5.4.8 and above.

### Workarounds

To manually enable TLS verification:

1. Open the NeuVector UI.
2. Navigate to **Settings > Configuration**.
3. In the **TLS Self-Signed Certificate Configuration** section, select **Enable TLS verification**.
4. (Optional) Upload or paste the **TLS self-signed certificate**.

### References

If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [NeuVector](https://github.com/neuvector/neuvector/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-neuvector/support-matrix/all-supported-versions/neuvector-v-all-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/#suse-security).

## References
- https://github.com/neuvector/neuvector/security/advisories/GHSA-4jj9-cgqc-x9h5
- https://nvd.nist.gov/vuln/detail/CVE-2025-66001
- https://github.com/neuvector/neuvector/commit/955904b5762f296d209bf395a5fcc7a40a53c424
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-66001
- https://github.com/neuvector/neuvector
