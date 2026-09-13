# [M] CVE-2021-47518

## Summary
Severity: Medium
Advisory: CVE-2021-47518
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47518
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: fix potential NULL pointer deref in nfc_genl_dump_ses_done

The done() netlink callback nfc_genl_dump_ses_done() should check if
received argument is non-NULL, because its allocation could fail earlier
in dumpit() (nfc_genl_dump_ses()).

## References
- https://git.kernel.org/stable/c/83ea620a1be840bf05089a5061fb8323ca42f38c
- https://git.kernel.org/stable/c/87cdb8789c38e44ae5454aafe277997c950d00ed
- https://git.kernel.org/stable/c/fae9705d281091254d4a81fa2da9d22346097dca
- https://git.kernel.org/stable/c/3b861a40325eac9c4c13b6c53874ad90617e944d
- https://git.kernel.org/stable/c/48fcd08fdbe05e35b650a252ec2a2d96057a1c7a
- https://git.kernel.org/stable/c/4cd8371a234d051f9c9557fcbb1f8c523b1c0d10
- https://git.kernel.org/stable/c/69bb79a8f5bb9f436b6f1434ca9742591b7bbe18
- https://git.kernel.org/stable/c/811a7576747760bcaf60502f096d1e6e91d566fa
