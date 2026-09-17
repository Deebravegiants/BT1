# [M] CVE-2023-29579

## Summary
Severity: Medium
Advisory: CVE-2023-29579
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-29579
Type: osv

## Details
yasm 1.3.0.55.g101bc was discovered to contain a stack overflow via the component yasm/yasm+0x43b466 in vsprintf. Note: This has been disputed by third parties who argue this is a bug and not a security issue because yasm is a standalone program not designed to run untrusted code.

## References
- https://github.com/yasm/yasm/issues/214
- https://github.com/z1r00/fuzz_vuln/blob/main/yasm/stack-buffer-overflow/yasm/readmd.md
