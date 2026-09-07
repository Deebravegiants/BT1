# [M] Electerm's full process.env exposed to renderer via window.pre.env

## Summary
Severity: Medium
Advisory: GHSA-37j4-88rp-2f6h
CVE: CVE-2026-43942
CWE: CWE-200, CWE-312
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-37j4-88rp-2f6h
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0

## Details
### Impact

The `getConstants()` IPC handler in `src/app/lib/ipc-sync.js` serialises the entire `process.env` object and sends it to the renderer. The data is stored as `window.pre.env` and is accessible from any JavaScript running in the renderer (e.g., via the DevTools console or a compromised webview context).

On developer and CI machines, `process.env` routinely contains secrets such as:

- `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN`
- `GITHUB_TOKEN` / `NPM_TOKEN`
- `OPENAI_API_KEY` / `DOCKER_AUTH`
- Internal service credentials, API keys, and database URLs

An attacker who achieves any JavaScript execution within the renderer—for example, through a malicious plugin, a cross-site scripting (XSS) flaw, or the terminal hyperlink execution chain—can trivially exfiltrate these secrets to a remote server, leading to cloud account compromise, supply chain attacks, and lateral movement. The exposure is visible even without any code execution by simply opening the "Info" modal in the application, though that requires local access.

### Patches

A patch is yet to be available.

### Workarounds

Until a patch is released:
- Avoid launching electerm with sensitive environment variables set. Use shell scripts or a dedicated terminal profile that clears secrets before starting the application.
- Do not install plugins from untrusted sources, and audit any installed plugins for network access.
- Keep the renderer context as locked down as possible: disable the remote debugging port, and do not paste untrusted code into the DevTools console.

### Resources
- [electerm GitHub Repository](https://github.com/electerm/electerm)
- [electerm Security Policy](https://github.com/electerm/electerm/security)
- Vulnerability details originally reported by external researcher (confirmed on v3.7.9, Win10).

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-37j4-88rp-2f6h
- https://nvd.nist.gov/vuln/detail/CVE-2026-43942
- https://github.com/electerm/electerm
