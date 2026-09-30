# [M] CVE-2021-47534

## Summary
Severity: Medium
Advisory: CVE-2021-47534
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47534
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vc4: kms: Add missing drm_crtc_commit_put

Commit 9ec03d7f1ed3 ("drm/vc4: kms: Wait on previous FIFO users before a
commit") introduced a global state for the HVS, with each FIFO storing
the current CRTC commit so that we can properly synchronize commits.

However, the refcounting was off and we thus ended up leaking the
drm_crtc_commit structure every commit. Add a drm_crtc_commit_put to
prevent the leakage.

## References
- https://git.kernel.org/stable/c/049cfff8d53a30cae3349ff71a4c01b7d9981bc2
- https://git.kernel.org/stable/c/53f9601e908d42481addd67cdb01a9288c611124
