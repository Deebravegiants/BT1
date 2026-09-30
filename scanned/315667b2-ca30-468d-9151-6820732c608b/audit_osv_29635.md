# [C] igb: cope with large MAX_SKB_FRAGS

## Summary
Severity: Critical
Advisory: CVE-2024-45030
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45030
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

igb: cope with large MAX_SKB_FRAGS

Sabrina reports that the igb driver does not cope well with large
MAX_SKB_FRAG values: setting MAX_SKB_FRAG to 45 causes payload
corruption on TX.

An easy reproducer is to run ssh to connect to the machine.  With
MAX_SKB_FRAGS=17 it works, with MAX_SKB_FRAGS=45 it fails.  This has
been reported originally in
https://bugzilla.redhat.com/show_bug.cgi?id=2265320

The root cause of the issue is that the driver does not take into
account properly the (possibly large) shared info size when selecting
the ring layout, and will try to fit two packets inside the same 4K
page even when the 1st fraglist will trump over the 2nd head.

Address the issue by checking if 2K buffers are insufficient.

## References
- https://git.kernel.org/stable/c/8aba27c4a5020abdf60149239198297f88338a8d
- https://git.kernel.org/stable/c/8ea80ff5d8298356d28077bc30913ed37df65109
- https://git.kernel.org/stable/c/b52bd8bcb9e8ff250c79b44f9af8b15cae8911ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45030.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45030
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
