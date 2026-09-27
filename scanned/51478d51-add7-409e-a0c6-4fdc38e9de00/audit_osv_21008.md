# [M] CVE-2021-3947

## Summary
Severity: Medium
Advisory: CVE-2021-3947
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-3947
Type: osv

## Details
A stack-buffer-overflow was found in QEMU in the NVME component. The flaw lies in nvme_changed_nslist() where a malicious guest controlling certain input can read out of bounds memory. A malicious user could use this flaw leading to disclosure of sensitive information.

## References
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20220318-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2021869
