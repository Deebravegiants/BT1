# [?] chore(wallet, docs, ts-sdk): Fix GHSA-43fc-jf86-j433: Upgrade axios to 1.13.5 (#10186)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-02-12
Source: https://github.com/iotaledger/iota/commit/c04074695cc5eaf5dfc110f7a16546a91ca7aff2
Type: security-commit

## Details
chore(wallet, docs, ts-sdk): Fix GHSA-43fc-jf86-j433: Upgrade axios to 1.13.5 (#10186)

# Description of change

Fixes high severity DoS vulnerability in axios <=1.13.4 where
`mergeConfig` allows `__proto__` key manipulation.

## Changes

- Upgraded axios from `^1.12.0` to `^1.13.5` in:
  - `apps/wallet/package.json`
  - `docs/site/package.json`
  - `sdk/ledgerjs-hw-app-iota/package.json`
- Updated `pnpm-lock.yaml`

## How the change has been tested

Verified axios 1.13.5 is installed in all three packages via `pnpm list
axios`. The vulnerable 1.12.0 version is no longer present in the
dependency tree.

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more
addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by
firewall rules:
>
> - `downloads.sentry-cdn.com`
> - Triggering command:
`/home/REDACTED/work/_temp/ghcca-node/node/bin/node node
./scripts/install.js` (dns block)
>
> If you need me to access, download, or install something from one of
these locations, you can either:
>
> - Configure [Actions setup
steps](https://gh.io/copilot/actions-setup-steps) to set up my
environment, which run before the firewall is enabled
> - Add the appropriate URLs or hosts to the custom allowlist in this
repository's [Copilot coding agent
settings](https://github.com/iotaledger/iota/settings/copilot/coding_agent)
(admins only)
>
> </details>

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>Fix GHSA-43fc-jf86-j433</issue_title>
> <issue_description>Fix
https://github.com/iotaledger/iota/actions/runs/21882852840/job/63169909161</issue_description>
> 
> <agent_instructions>Run pnpm audit --prod --audit-level high
>
┌─────────────────────┬────────────────────────────────────────────────────────┐
> │ high │ Axios is Vulnerable to Denial of Service via __proto__ │
> │ │ Key in mergeConfig │
>
├─────────────────────┼────────────────────────────────────────────────────────┤
> │ Package │ axios │
>
├─────────────────────┼────────────────────────────────────────────────────────┤
> │ Vulnerable versions │ <=1.13.4 │
>
├─────────────────────┼────────────────────────────────────────────────────────┤
> │ Patched versions │ >=1.13.5 │
>
├─────────────────────┼────────────────────────────────────────────────────────┤
> │ Paths │ │
>
├─────────────────────┼────────────────────────────────────────────────────────┤
> │ More info │ https://github.com/advisories/GHSA-43fc-jf86-j433 │
>
└─────────────────────┴────────────────────────────────────────────────────────┘
> 28 vulnerabilities found
> Severity: 8 low | 18 moderate | 2 high
> </agent_instructions>
> 
> ## Comments on the Issue (you are @copilot in this section)
> 
> <comments>
> </comments>
> 


</details>



<!-- START COPILOT CODING AGENT SUFFIX -->

- Fixes iotaledger/iota#10185

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! Share your thoughts on Copilot coding agent in
our [2 minute survey](https://gh.io/copilot-coding-agent-survey).

Co-authored-by: marc2332 <mespinsanz@gmail.com>

### .changeset/thick-spiders-hope.md
```diff
@@ -0,0 +1,5 @@
+---
+'@iota/ledgerjs-hw-app-iota': patch
+---
+
+Update axios to 1.13.5
```

### apps/wallet/package.json
```diff
@@ -124,7 +124,7 @@
         "@sentry/browser": "^7.120.3",
         "@tanstack/react-query": "^5.50.1",
         "@tanstack/react-query-persist-client": "^5.40.1",
-        "axios": "^1.12.0",
+        "axios": "^1.13.5",
         "bignumber.js": "^9.1.1",
         "buffer": "^6.0.3",
         "class-variance-authority": "^0.7.0",
```

### docs/site/package.json
```diff
@@ -43,7 +43,7 @@
     "@saucelabs/theme-github-codeblock": "^0.3.0",
     "@tanstack/react-query": "^5.50.1",
     "autoprefixer": "^10.4.19",
-    "axios": "^1.12.0",
+    "axios": "^1.13.5",
     "clsx": "^2.1.1",
     "docusaurus-plugin-openapi-docs": "^4.3.7",
     "docusaurus-theme-openapi-docs": "^4.3.7",
```

### sdk/ledgerjs-hw-app-iota/package.json
```diff
@@ -65,7 +65,7 @@
         "@ledgerhq/hw-transport-node-speculos-http": "^6.30.2",
         "@size-limit/preset-small-lib": "^11.1.4",
         "@types/node": "^20.14.10",
-        "axios": "^1.12.0",
+        "axios": "^1.13.5",
         "size-limit": "^11.1.4",
         "typescript": "^5.5.3",
         "vitest": "^2.1.9"
```
