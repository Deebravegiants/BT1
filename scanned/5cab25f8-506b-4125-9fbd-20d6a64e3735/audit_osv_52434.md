# [M] CVE-2021-47445

## Summary
Severity: Medium
Advisory: CVE-2021-47445
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47445
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: Fix null pointer dereference on pointer edp

The initialization of pointer dev dereferences pointer edp before
edp is null checked, so there is a potential null pointer deference
issue. Fix this by only dereferencing edp after edp has been null
checked.

Addresses-Coverity: ("Dereference before null check")

## References
- https://git.kernel.org/stable/c/91a340768b012f5b910a203a805b97a345b3db37
- https://git.kernel.org/stable/c/bacac7d26849c8e903ceb7466d9ce8dc3c2797eb
- https://git.kernel.org/stable/c/f175b9a83e5c252d7c74acddc792840016caae0a
- https://git.kernel.org/stable/c/f302be08e3de94db8863a0b2958b2bb3e8e998e6
- https://git.kernel.org/stable/c/0cd063aa0a09822cc1620fc59a67fe2f9f6338ac
- https://git.kernel.org/stable/c/2133c4fc8e1348dcb752f267a143fe2254613b34
- https://git.kernel.org/stable/c/46c8ddede0273d1d132beefa9de8b820326982be
- https://git.kernel.org/stable/c/7f642b93710b6b1119bdff90be01e6b5a2a5d669
