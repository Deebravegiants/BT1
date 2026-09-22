# [H] Race condition when flushing input stream leads to permission prompt bypass

## Summary
Severity: High
Advisory: CVE-2024-32477
Aliases: GHSA-95cj-3hr2-7j5j
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-18
Source: https://osv.dev/vulnerability/CVE-2024-32477
Type: osv

## Details
Deno is a JavaScript, TypeScript, and WebAssembly runtime with secure defaults. By using ANSI escape sequences and a race between `libc::tcflush(0, libc::TCIFLUSH)` and reading standard input, it's possible to manipulate the permission prompt and force it to allow an unsafe action regardless of the user input. Some ANSI escape sequences act as a info request to the master terminal emulator and the terminal emulator sends back the reply in the PTY channel. standard streams also use this channel to send and get data. For example the `\033[6n` sequence requests the current cursor position. These sequences allow us to append data to the standard input of Deno. This vulnerability allows an attacker to bypass Deno permission policy.  This vulnerability is fixed in 1.42.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32477.json
- https://github.com/denoland/deno/security/advisories/GHSA-95cj-3hr2-7j5j
- https://nvd.nist.gov/vuln/detail/CVE-2024-32477
