# [M] CVE-2021-46928

## Summary
Severity: Medium
Advisory: CVE-2021-46928
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46928
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

parisc: Clear stale IIR value on instruction access rights trap

When a trap 7 (Instruction access rights) occurs, this means the CPU
couldn't execute an instruction due to missing execute permissions on
the memory region.  In this case it seems the CPU didn't even fetched
the instruction from memory and thus did not store it in the cr19 (IIR)
register before calling the trap handler. So, the trap handler will find
some random old stale value in cr19.

This patch simply overwrites the stale IIR value with a constant magic
"bad food" value (0xbaadf00d), in the hope people don't start to try to
understand the various random IIR values in trap 7 dumps.

## References
- https://git.kernel.org/stable/c/484730e5862f6b872dca13840bed40fd7c60fa26
- https://git.kernel.org/stable/c/d01e9ce1af6116f812491d3d3873d204f10ae0b8
- https://git.kernel.org/stable/c/e96373f0a5f484bc1e193f9951dcb3adf24bf3f7
