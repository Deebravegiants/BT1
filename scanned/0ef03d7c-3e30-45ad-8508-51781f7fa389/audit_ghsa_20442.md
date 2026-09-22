# [M] Potential exposure of tokens to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-7w54-gp8x-f33m
CVE: CVE-2022-21671
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-7w54-gp8x-f33m
Type: github-advisory

## Affected
- npm: `@replit/crosis` — affected >=0 <7.3.1

## Details
### Impact

When using this library as a way to programmatically communicate with Replit in a standalone fashion, if there are multiple failed attempts to contact Replit through a WebSocket, the library will attempt to communicate using a fallback poll-based proxy. The URL of the proxy has changed, so any communication done to the previous URL could potentially reach a server that is outside of Replit's control and the token used to connect to the Repl could be obtained by an attacker, leading to full compromise of that Repl (not of the account).

### Patches

This was patched in 7.3.1, by updating the address of the fallback WebSocket polling proxy to the new one.

### Workarounds

Specify the new address for the polling host (`gp-v2.replit.com`) in the `ConnectArgs`:

```typescript
const connectOptions: ConnectArgs = {
  // ...
  pollingHost: 'gp-v2.replit.com',
};
client.connect(connectOptions);
```

### For more information

Thanks to https://hackerone.com/orlserg for disclosing this.

If you have any questions or comments about this advisory:
* Open an issue in [replit/crosis](https://github.com/replit/crosis)
* Email us at [security@replit.com](mailto:security@replit.com)

## References
- https://github.com/replit/crosis/security/advisories/GHSA-7w54-gp8x-f33m
- https://nvd.nist.gov/vuln/detail/CVE-2022-21671
- https://github.com/replit/crosis/commit/e44b6a8f5fa28cb2872e3c19bb8a205bb5bfc281
- https://github.com/replit/crosis
