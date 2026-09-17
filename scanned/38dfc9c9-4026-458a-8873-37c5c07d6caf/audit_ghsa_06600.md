# [H] OpenClaw: Non-owner chat senders could issue device-pairing bootstrap codes

## Summary
Severity: High
Advisory: GHSA-xr4f-mjxj-w6w5
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-xr4f-mjxj-w6w5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.4

## Details
### Summary

The bundled device-pair plugin exposed `/pair` on normal chat command surfaces. In affected releases, authorized non-owner chat senders could issue device-pairing bootstrap codes without having owner, admin, or pairing scope.

This issue does not affect unauthenticated users. The caller must already be allowed to send commands to the agent through a configured chat channel.

### Affected configurations

This affects deployments where the bundled device-pair plugin is enabled and a non-owner sender is authorized to use normal chat commands, such as in a configured Telegram, Discord, or Slack agent.

### Impact

A non-owner authorized sender could create a setup code and use it before expiry to enroll a device with operator/node capabilities. That device would then retain persistent credentials until removed.

### Patched Versions

The first stable patched version is `2026.5.4`.

### Mitigations

Upgrade to `openclaw@2026.5.4` or later. Review paired devices and remove any unexpected entries. In shared chat channels, keep command access limited to users who should be allowed to manage device pairing.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xr4f-mjxj-w6w5
- https://github.com/openclaw/openclaw
