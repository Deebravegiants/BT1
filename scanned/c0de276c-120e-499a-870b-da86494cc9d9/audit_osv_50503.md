# [H] CVE-2020-16094

## Summary
Severity: High
Advisory: CVE-2020-16094
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-28
Source: https://osv.dev/vulnerability/CVE-2020-16094
Type: osv

## Details
In imap_scan_tree_recursive in Claws Mail through 3.17.6, a malicious IMAP server can trigger stack consumption because of unlimited recursion into subdirectories during a rebuild of the folder tree.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3CRKHUOVTJBHT53J4CYU53PXYYQKSGEA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JUBLHUG2UCXVABAGN5FVTD3AB3YKE5NN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YNJIXYDMSXYDII4ERMQ4EEKZX64U3QR4/
- https://www.thewildbeast.co.uk/claws-mail/bugzilla/show_bug.cgi?id=4313
