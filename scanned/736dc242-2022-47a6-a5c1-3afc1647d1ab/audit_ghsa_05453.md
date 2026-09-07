# [H] Deno has an incomplete fix for command-injection prevention on Windows — case-insensitive extension bypass

## Summary
Severity: High
Advisory: GHSA-m3c4-prhw-mrx6
CVE: CVE-2026-22864
CWE: CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-m3c4-prhw-mrx6
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.5.6

## Details
### Summary
A prior patch aimed to block spawning Windows batch/shell files by returning an error when a spawned path’s extension matched `.bat` or `.cmd`. That check performs a case-sensitive comparison against lowercase literals and therefore can be bypassed when the extension uses alternate casing (for example `.BAT, .Bat`, etc.).

### POC
```javascript
const command = new Deno.Command('./test.BAT', {
  args: ['&calc.exe'],
});
const child = command.spawn();
```
This causes `calc.exe` to be launched; see the attached screenshot for evidence.

**Patched in `CVE-2025-61787` — prevents execution of `.bat` and `.cmd` files:**
![photo_2025-10-10 02 27 23](https://github.com/user-attachments/assets/43df25e2-e2e1-48aa-8060-cb0a22637f1f)

**Bypass of the patched vulnerability:**
![photo_2025-10-10 02 27 25](https://github.com/user-attachments/assets/2be1afb4-84a1-4883-8e18-6a174fdd3615)


### Impact
The script launches calc.exe on Windows, demonstrating that passing user-controlled arguments to a spawned batch script can result in command-line injection.

### Mitigation

Users should update to Deno v2.5.6 or newer.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-m3c4-prhw-mrx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-22864
- https://github.com/denoland/deno
- https://github.com/denoland/deno/releases/tag/v2.5.6
