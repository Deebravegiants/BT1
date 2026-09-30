# [M] MariaDB has Cleartext Transmission of Sensitive Information and Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-42r5-vhpq-m858
CVE: CVE-2026-55854
CWE: CWE-319, CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-42r5-vhpq-m858
Type: github-advisory

## Affected
- npm: `mariadb` — affected >=0 <3.2.4
- npm: `mariadb` — affected >=3.3.0 <3.3.3
- npm: `mariadb` — affected >=3.4.0 <3.4.6
- npm: `mariadb` — affected >=3.5.0 <3.5.3

## Details
### Summary

When PAM (dialog) authentication is used, the connector can be coerced into sending the account password in cleartext over an insecure connection. A hostile or man-in-the-middle server can trigger this with the default configuration, disclosing the user's password.

### Details

The mysql_clear_password plugin is gated behind a secure connection: the driver refuses to transmit the password in cleartext over plain TCP. The sibling PAM plugin handler (SendPamAuthPacketFactory, server-side plugin name dialog) did not override that gate and inherited the default value false, so it was not subject to the same secure-transport requirement.

As a result, a hostile or man-in-the-middle server can issue an Authentication Switch Request for the dialog plugin over plain TCP, and the driver responds with the user's password in cleartext. With the default configuration (sslMode=DISABLE, restrictedAuth=null) this is reachable with no non-default options.

### Am I affected?

You are affected if all of the following hold:

You use mariadb Connector/Node.js at a version below the patched release(s).
Connections can occur over an insecure transport: plain TCP (sslMode=DISABLE), or a TLS mode that establishes server identity only via self-signed-certificate fingerprint validation.
An attacker can occupy an on-path (MITM) position, or otherwise cause the client to connect to a server they control, and present an Authentication Switch Request for the dialog plugin.

Connections over properly verified TLS or a local Unix socket are not exposed to this vector.

### Impact

Disclosure of the authenticating account's password in cleartext to an on-path or hostile server. The captured credentials can then be reused to authenticate to the database (and, if reused elsewhere, beyond it).

### Patches

Fixed in 3.2.4, 3.3.3, 3.4.6, and 3.5.3. Upgrade to the patched release on your branch (3.5.x → 3.5.3, 3.4.x → 3.4.6, 3.3.x → 3.3.3, 3.2.x and earlier → 3.2.4). PAM (dialog) is now treated exactly like mysql_clear_password: it may only run over a secure transport. SendPamAuthPacketFactory overrides the secure-required flag to true, and the authentication dispatcher permits a secure-required plugin only when the connection is TLS or a local Unix socket. The pre-existing check that blocks non-MITM-proof plugins when server identity relies solely on self-signed-certificate fingerprint validation continues to apply. Net effect: PAM is allowed over TLS or a Unix socket, and rejected over plain TCP or fingerprint-only connections.

### Workarounds

If you cannot upgrade immediately:

* Restrict the permitted authentication plugins via restrictedAuth so dialog cannot be negotiated over an insecure transport.
Avoid PAM (dialog) authentication over plain TCP.

###Credit

Reported by Yalguun Tumenkhuu ([@fg0x0](https://github.com/fg0x0/)).

## References
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/security/advisories/GHSA-42r5-vhpq-m858
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/commit/29733403cfe6519cdfe9c36c93765a468fbe285d
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/commit/53b304264df84496d331dba2765c3634602f342e
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/commit/9781de636841d34afdd08d81dd07d43edb82f85c
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/commit/fbc159c2c8bd18c2db2d2e6587ab3020bbda64b6
- https://github.com/mariadb-corporation/mariadb-connector-nodejs
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/releases/tag/3.2.4
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/releases/tag/3.3.3
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/releases/tag/3.4.6
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/releases/tag/3.5.3
- https://jira.mariadb.org/browse/CONJS-353
