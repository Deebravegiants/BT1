# [C] openvpn-auth-oauth2 returns FUNC_SUCCESS on client-deny, allowing unauthenticated VPN access

## Summary
Severity: Critical
Advisory: GHSA-246w-jgmq-88fg
CVE: CVE-2026-41070
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-246w-jgmq-88fg
Type: github-advisory

## Affected
- Go: `github.com/jkroepke/openvpn-auth-oauth2` — affected >=1.26.3 <1.27.3

## Details
# Summary

When `openvpn-auth-oauth2` is deployed in the **experimental plugin mode** (shared library loaded by OpenVPN via the `plugin` directive), clients that do not support WebAuth/SSO (e.g., the `openvpn` CLI on Linux) are incorrectly admitted to the VPN despite being denied by the authentication logic. **The default management-interface mode is not affected** because it does not use the OpenVPN plugin return-code mechanism.

# Impact

**Authentication bypass — any VPN client that does not advertise WebAuth/SSO support (`IV_SSO=webauth`) is granted full network access without completing OIDC authentication.**

This affects only deployments running the **experimental plugin mode** in versions 1.26.3 through 1.27.2. The default and recommended deployment via the management interface is **not affected**.

An unauthenticated attacker can connect to the OpenVPN server using any standard OpenVPN client that does not support webauth (e.g., the Linux `openvpn` CLI). The plugin correctly issues a `client-deny` command via the management interface, but returns `OPENVPN_PLUGIN_FUNC_SUCCESS` (status=0) to OpenVPN. Because the `auth_control_file` content is only consulted when the plugin returns `FUNC_DEFERRED`, OpenVPN interprets status=0 as "authentication passed" and admits the client — granting full access to the internal network behind the VPN.


## Root Cause

In `lib/openvpn-auth-oauth2/openvpn/handle.go`, the `ClientAuthDeny` branch of `handleAuthUserPassVerify` wrote `"0"` (deny) to the `auth_control_file` but returned `OPENVPN_PLUGIN_FUNC_SUCCESS`. OpenVPN only reads the `auth_control_file` when the plugin returns `FUNC_DEFERRED`; a synchronous `FUNC_SUCCESS` return is treated as immediate approval regardless of file contents.

**Before fix:**
```go
case management.ClientAuthDeny:
    // ... writes "0" to auth_control_file ...
    if err := openVPNClient.WriteToAuthFile("0"); err != nil {
        // only returned ERROR on write failure
        return c.OpenVPNPluginFuncError
    }
    return c.OpenVPNPluginFuncSuccess  // ← BUG: OpenVPN sees this as "auth passed"
```

**After fix (commit [`36f69a6`](https://github.com/jkroepke/openvpn-auth-oauth2/commit/36f69a6c67c1054da7cbfa04ced3f0555127c8f2)):**
```go
case management.ClientAuthDeny:
    // ... writes "0" to auth_control_file ...
    if err := openVPNClient.WriteToAuthFile("0"); err != nil {
        logger.ErrorContext(p.ctx, "write to auth file", slog.Any("err", err))
    }
    return c.OpenVPNPluginFuncError  // ← FIX: OpenVPN now correctly rejects the client
```

# Patches

This vulnerability is fixed in **v1.27.3**. Users of the experimental plugin mode should upgrade immediately.

- **Fix commit:** [`36f69a6`](https://github.com/jkroepke/openvpn-auth-oauth2/commit/36f69a6c67c1054da7cbfa04ced3f0555127c8f2)
- **Fix PR:** [#829](https://github.com/jkroepke/openvpn-auth-oauth2/pull/829)

# Workarounds

- **Switch to standalone management client mode** (the default, non-plugin deployment). This mode is not affected by the vulnerability because authentication decisions are communicated entirely through the management interface protocol, not through the plugin return code.
- **Restrict VPN access at the network level** to only clients known to support WebAuth/SSO (e.g., OpenVPN Connect 3+), although this is difficult to enforce reliably and is not recommended as a sole mitigation.

## References
- https://github.com/jkroepke/openvpn-auth-oauth2/security/advisories/GHSA-246w-jgmq-88fg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41070
- https://github.com/jkroepke/openvpn-auth-oauth2/pull/829
- https://github.com/jkroepke/openvpn-auth-oauth2/commit/36f69a6c67c1054da7cbfa04ced3f0555127c8f2
- https://github.com/OpenVPN/openvpn/blob/master/include/openvpn-plugin.h.in
- https://github.com/OpenVPN/openvpn3/blob/master/doc/webauth.md
- https://github.com/jkroepke/openvpn-auth-oauth2
- https://github.com/jkroepke/openvpn-auth-oauth2/releases/tag/v1.27.3
