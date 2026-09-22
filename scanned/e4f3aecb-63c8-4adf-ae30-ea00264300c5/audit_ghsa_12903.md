# [H] Deno is vulnerable to race condition via interactive permission prompt spoofing

## Summary
Severity: High
Advisory: GHSA-mc52-jpm2-cqh6
CVE: CVE-2023-22499
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-mc52-jpm2-cqh6
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.9.0 <1.29.3

## Details
### Impact

Multi-threaded programs were able to spoof interactive permission prompt by rewriting the prompt to suggest that program is waiting on user confirmation to unrelated action. 

A malicious program could clear the terminal screen after permission prompt was shown and write a generic message like so:
```
// Expected prompt
⚠️  ┌ Deno requests read access to "./log.txt".
   ├ Requested by `Deno.open()` API
   ├ Run again with --allow-read to bypass this prompt.
   └ Allow? [y/n] (y = yes, allow; n = no, deny) >

// Prompt that users would see
Do you want to continue?
```

This situation impacts users who use Web Worker API and relied on interactive permission prompt. The reproduction is very timing sensitive and can’t be reliably reproduced on every try.

This problem can not be exploited on systems that do not attach an interactive prompt (for example headless servers). 

### Patches

The problem has been fixed in Deno v1.29.3; it is recommended all users update to this version.

### Workarounds

Run with `--no-prompt` flag to disable interactive permission prompts.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-mc52-jpm2-cqh6
- https://nvd.nist.gov/vuln/detail/CVE-2023-22499
- https://github.com/denoland/deno/pull/17392
- https://github.com/denoland/deno
