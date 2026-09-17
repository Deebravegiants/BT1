# [M] CVE-2017-12193

## Summary
Severity: Medium
Advisory: CVE-2017-12193
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-22
Source: https://osv.dev/vulnerability/CVE-2017-12193
Type: osv

## Details
The assoc_array_insert_into_terminal_node function in lib/assoc_array.c in the Linux kernel before 4.13.11 mishandles node splitting, which allows local users to cause a denial of service (NULL pointer dereference and panic) via a crafted application, as demonstrated by the keyring key type, and key addition and link creation operations.

## References
- https://usn.ubuntu.com/3698-1/
- https://usn.ubuntu.com/3698-2/
- http://www.securityfocus.com/bid/101678
- https://access.redhat.com/errata/RHSA-2018:0151
- https://bugzilla.redhat.com/show_bug.cgi?id=1501215
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.11
- https://github.com/torvalds/linux/commit/ea6789980fdaa610d7eb63602c746bf6ec70cd2b
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ea6789980fdaa610d7eb63602c746bf6ec70cd2b
