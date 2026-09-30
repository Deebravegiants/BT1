# [H] CVE-2017-7374

## Summary
Severity: High
Advisory: CVE-2017-7374
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-31
Source: https://osv.dev/vulnerability/CVE-2017-7374
Type: osv

## Details
Use-after-free vulnerability in fs/crypto/ in the Linux kernel before 4.10.7 allows local users to cause a denial of service (NULL pointer dereference) or possibly gain privileges by revoking keyring keys being used for ext4, f2fs, or ubifs encryption, causing cryptographic transform objects to be freed prematurely.

## References
- http://www.securityfocus.com/bid/97308
- https://source.android.com/security/bulletin/2017-10-01
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.7
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1b53cf9815bb4744958d41f3795d5d5a1d365e2d
- https://github.com/torvalds/linux/commit/1b53cf9815bb4744958d41f3795d5d5a1d365e2d
