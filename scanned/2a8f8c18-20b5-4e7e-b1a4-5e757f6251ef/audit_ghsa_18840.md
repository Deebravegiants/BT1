# [H] Kottster app reinitialization can be re-triggered allowing command injection in development mode

## Summary
Severity: High
Advisory: GHSA-j3w7-9qc3-g96p
CVE: CVE-2025-62713
CWE: CWE-284, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-j3w7-9qc3-g96p
Type: github-advisory

## Affected
- npm: `@kottster/server` — affected >=3.2.0 <3.3.2

## Details
### Impact

**Development mode only**. Kottster contains a pre-authentication remote code execution (RCE) vulnerability when running in development mode.

The vulnerability combines two issues:
1. The `initApp` action can be called repeatedly without checking if the app is already initialized, allowing attackers to create a new root admin account and obtain a JWT token
2. The `installPackagesForDataSource` action uses unescaped command arguments, enabling command injection

An attacker with access to a locally running development instance can chain these vulnerabilities to:
- Reinitialize the application and receive a JWT token for a new root account
- Use this token to authenticate
- Execute arbitrary system commands through `installPackagesForDataSource`

**Production deployments were never affected.**

### Patches

Fixed in [v3.3.2](https://github.com/kottster/kottster/releases/tag/v3.3.2).

Specifically, `@kottster/server` [v3.3.2](https://www.npmjs.com/package/@kottster/server/v/3.3.2) and `@kottster/cli` [v3.3.2](https://www.npmjs.com/package/@kottster/cli/v/3.3.2) address this vulnerability.

We recommend developers using earlier versions of `@kottster/server` and `@kottster/cli` update all the core packages to latest release:

```
npm install @kottster/common@latest @kottster/cli@latest @kottster/server@latest @kottster/react@latest
```

### Workarounds

- Do not expose development servers to public networks or untrusted users
- Use production mode for any deployment accessible from outside trusted environments

### Credit

We sincerely thank Jeongwon Jo ([@P0cas](https://github.com/P0cas)) from **RedAlert** for discovering and responsibly disclosing this vulnerability.

## References
- https://github.com/kottster/kottster/security/advisories/GHSA-j3w7-9qc3-g96p
- https://nvd.nist.gov/vuln/detail/CVE-2025-62713
- https://github.com/kottster/kottster/commit/0a7d24922a23aac98372155348787670937eef89
- https://github.com/kottster/kottster
