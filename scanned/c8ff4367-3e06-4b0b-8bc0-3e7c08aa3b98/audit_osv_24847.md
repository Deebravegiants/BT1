# [H] Rizin has stack-based buffer overflow when parsing GDB registers profile files

## Summary
Severity: High
Advisory: CVE-2023-27590
Aliases: GHSA-rqcp-m8m2-jcqf
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-14
Source: https://osv.dev/vulnerability/CVE-2023-27590
Type: osv

## Details
Rizin is a UNIX-like reverse engineering framework and command-line toolset. In version 0.5.1 and prior, converting a GDB registers profile file into a Rizin register profile can result in a stack-based buffer overflow when the `name`, `type`, or `groups` fields have longer values than expected. Users opening untrusted GDB registers files (e.g. with the `drpg` or `arpg` commands) are affected by this flaw. Commit d6196703d89c84467b600ba2692534579dc25ed4 contains a patch for this issue. As a workaround, review the GDB register profiles before loading them with `drpg`/`arpg` commands.

## References
- https://github.com/rizinorg/rizin/blob/3a7d5116244beb678ad9950bb9dd27d28ed2691f/librz/reg/profile.c#L514
- https://github.com/rizinorg/rizin/blob/3a7d5116244beb678ad9950bb9dd27d28ed2691f/librz/reg/profile.c#L545
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WW3JXI4TIJIR7PGFP74SN7GQYHW2F46Y/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27590.json
- https://github.com/rizinorg/rizin/security/advisories/GHSA-rqcp-m8m2-jcqf
- https://nvd.nist.gov/vuln/detail/CVE-2023-27590
- https://github.com/rizinorg/rizin/commit/d6196703d89c84467b600ba2692534579dc25ed4
- https://github.com/rizinorg/rizin/pull/3422
