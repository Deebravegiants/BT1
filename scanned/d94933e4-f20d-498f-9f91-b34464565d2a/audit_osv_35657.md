# [M] Out-of-bounds write in Xtensa llext PLT relocation from malformed ELF (CWE-787)

## Summary
Severity: Medium
Advisory: CVE-2026-12235
Aliases: GHSA-xv9q-6mrf-8j49
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-12235
Type: osv

## Details
The Linkable Loadable Extensions (llext) subsystem mis-handles PLT/RELA relocation entries when linking a relocatable (partially-linked) ELF extension. In llext_link_plt() (subsys/llext/llext_link.c), the relocatable branch (tgt != NULL, the path used for Xtensa relocatable objects) computed the patch address as ext->mem[LLEXT_MEM_TEXT] - text.sh_offset + rela.r_offset + tgt->sh_offset and then performed the relocation write there without validating rela.r_offset. Its sibling shared/dynamic branch already rejected out-of-range offsets via llext_file_offset().

rela.r_offset is read directly from the ELF's RELA table, so a crafted entry with an offset larger than the target section makes the write land arbitrarily far outside the extension's text buffer. The result is an attacker-influenced out-of-bounds write (the location via r_offset, the written value being the resolved symbol address) performed in supervisor context at link time, before any extension code runs.

The path is reached from llext_load() whenever an application loads an attacker-influenced ELF extension on Xtensa with writable storage; llext is documented to accept extensions of untrusted origin. Impact is supervisor-context memory corruption (integrity and availability loss, and a sandbox-boundary escape for user-mode extensions). Exploitation is gated by the Xtensa relocatable PLT path and writable storage, and turning the out-of-range write into a useful primitive is non-trivial.

The fix adds a bound check rejecting any RELA entry whose r_offset >= tgt->sh_size, mirroring the existing validation in the shared branch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12235.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-xv9q-6mrf-8j49
- https://nvd.nist.gov/vuln/detail/CVE-2026-12235
- https://github.com/zephyrproject-rtos/zephyr/commit/106540afbd22087ad40b90f53fb22657754a719e
- https://github.com/zephyrproject-rtos/zephyr
