# [M] CVE-2019-12067

## Summary
Severity: Medium
Advisory: CVE-2019-12067
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2019-12067
Type: osv

## Details
The ahci_commit_buf function in ide/ahci.c in QEMU allows attackers to cause a denial of service (NULL dereference) when the command header 'ad->cur_cmd' is null.

## References
- https://security-tracker.debian.org/tracker/CVE-2019-12067
- https://security.netapp.com/advisory/ntap-20210727-0001/
- https://bugzilla.suse.com/show_bug.cgi?id=1145642
- https://lists.gnu.org/archive/html/qemu-devel/2019-08/msg01358.html
- https://lists.gnu.org/archive/html/qemu-devel/2019-08/msg01487.html
