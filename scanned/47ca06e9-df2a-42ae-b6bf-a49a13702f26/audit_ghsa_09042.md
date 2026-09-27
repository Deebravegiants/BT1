# [M] Lemur: LDAP Authentication Globally Disables TLS Certificate Verification When LDAP_USE_TLS Is Enabled

## Summary
Severity: Medium
Advisory: GHSA-vr7c-r5gj-j3w5
CVE: CVE-2026-44305
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-vr7c-r5gj-j3w5
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.0

## Details
## Description

### Overview

When LDAP TLS is enabled (`LDAP_USE_TLS = True`), Lemur's LDAP authentication module unconditionally disables TLS certificate verification at the **global** `ldap` module level. This allows a man-in-the-middle attacker positioned between Lemur and the LDAP server to intercept all authentication credentials.

### Vulnerable Code

**Location:** `lemur/auth/ldap.py`, `_bind()` method, line ~172

```python
if self.ldap_use_tls:
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
```

Key issues:

1. `ldap.set_option()` is a **global** call (as opposed to `self.ldap_client.set_option()`), meaning it disables TLS verification for the entire Python process, not just this connection
2. `OPT_X_TLS_NEVER` means no certificate validation is performed whatsoever — self-signed, expired, wrong hostname, and revoked certificates are all silently accepted
3. There is no configuration option to override this behavior — TLS verification is always disabled when TLS is enabled

### Impact

A network-positioned attacker (man-in-the-middle) between Lemur and the LDAP server can:

- **Intercept all LDAP credentials** (usernames and plaintext passwords) for every user who authenticates
- **Modify LDAP responses** to inject arbitrary group memberships, granting admin access
- **Compromise the entire PKI infrastructure** managed by Lemur, since authentication controls access to certificates and private keys

This is particularly severe because Lemur is a certificate management system — the tool designed to manage TLS security is itself vulnerable to a TLS attack.

### Steps to Reproduce

1. Deploy Lemur with LDAP TLS enabled:
   ```python
   LDAP_AUTH = True
   LDAP_USE_TLS = True
   LDAP_BIND_URI = "ldaps://dc.corp.example.com"
   ```

2. Intercept the LDAP connection using a TLS proxy (e.g., `mitmproxy` or `stunnel`):
   ```bash
   # Generate a self-signed certificate
   openssl req -x509 -newkey rsa:2048 -keyout mitm.key -out mitm.crt -days 1 -nodes -subj "/CN=mitm"

   # Proxy LDAP traffic
   stunnel -d 0.0.0.0:636 -r real-ldap-server:636 -p mitm.pem
   ```

3. Point Lemur's `LDAP_BIND_URI` at the proxy (or perform ARP spoofing/DNS hijacking)

4. Observe that Lemur connects without any certificate verification error

5. All credentials are visible in the proxy's TLS session

### Remediation

Remove the global TLS verification bypass and default to strict verification:

```python
if self.ldap_use_tls:
    # Use instance-level option, not global
    self.ldap_client.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
    self.ldap_client.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    if self.ldap_cacert_file:
        self.ldap_client.set_option(ldap.OPT_X_TLS_CACERTFILE, self.ldap_cacert_file)
```

If backward compatibility is needed, make it configurable with a secure default:

```python
tls_require_cert = current_app.config.get("LDAP_TLS_REQUIRE_CERT", ldap.OPT_X_TLS_DEMAND)
self.ldap_client.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, tls_require_cert)
```

### Resources

- CWE-295: https://cwe.mitre.org/data/definitions/295.html
- python-ldap TLS documentation: https://www.python-ldap.org/en/python-ldap-3.4.0/reference/ldap.html#tls-options

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-vr7c-r5gj-j3w5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44305
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.0
- https://www.python-ldap.org/en/python-ldap-3.4.0/reference/ldap.html#tls-options
