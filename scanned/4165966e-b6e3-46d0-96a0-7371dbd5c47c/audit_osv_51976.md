# [M] CVE-2021-46918

## Summary
Severity: Medium
Advisory: CVE-2021-46918
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46918
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: clear MSIX permission entry on shutdown

Add disabling/clearing of MSIX permission entries on device shutdown to
mirror the enabling of the MSIX entries on probe. Current code left the
MSIX enabled and the pasid entries still programmed at device shutdown.

## References
- https://git.kernel.org/stable/c/6df0e6c57dfc064af330071f372f11aa8c584997
- https://git.kernel.org/stable/c/c84b8982d7aa9b4717dc36a1c6cbc93ee153b500
