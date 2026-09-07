# [H] Flowise: RBAC Bypass Leading to Unauthorized Workspace Variables Disclosure

## Summary
Severity: High
Advisory: GHSA-8r8h-6vcc-xhrv
CVE: CVE-2026-70471
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-8r8h-6vcc-xhrv
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
## Finding — Unauthorized Workspace Variables disclosure via $vars injection (bypasses variables:view)

  ### What’s wrong (code locations)

  - Variables for the active workspace are fetched without checking “variables:view” at this call site: flowise-src/
    packages/components/src/utils.ts:932
  - Runtime variables are resolved from server environment variables: flowise-src/packages/components/src/utils.ts:976
  - $vars is always injected into the code execution sandbox: flowise-src/packages/components/src/utils.ts:1782
  - The official Variables API is permission-protected (contrast): flowise-src/packages/server/src/routes/variables/
    index.ts:11

  ### Why it is a privilege boundary bypass

  A user/API key might be denied variables:view (and the /api/v1/variables route enforces it), but they can still:

  - call /api/v1/node-custom-function (Finding 1)
  - and have $vars pre-populated with all variables for the workspace, including runtime values from process.env

  ### What data is exposed

  Inside the custom JS context, $vars contains a flat map of:

  - Variable.name -> Variable.value for static variables, and
  - Variable.name -> process.env[Variable.name] for runtime variables (type === 'runtime')

  This can expose secrets such as database passwords, JWT secrets, SMTP passwords, cloud keys, etc., depending on what
  the workspace Variables are configured to map.

  ### Recommended fix (minimum)

  - Do not inject $vars unless the caller is authorized:
      - enforce variables:view before injecting $vars, or
      - inject only an explicit allowlist of variables needed for the function
  - Consider disabling or heavily restricting type=runtime variables in self-hosted environments (or restrict which env
    keys may be mapped).

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-8r8h-6vcc-xhrv
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
