# [H] vhost_vdpa: assign irq bypass producer token correctly

## Summary
Severity: High
Advisory: CVE-2024-47748
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47748
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost_vdpa: assign irq bypass producer token correctly

We used to call irq_bypass_unregister_producer() in
vhost_vdpa_setup_vq_irq() which is problematic as we don't know if the
token pointer is still valid or not.

Actually, we use the eventfd_ctx as the token so the life cycle of the
token should be bound to the VHOST_SET_VRING_CALL instead of
vhost_vdpa_setup_vq_irq() which could be called by set_status().

Fixing this by setting up irq bypass producer's token when handling
VHOST_SET_VRING_CALL and un-registering the producer before calling
vhost_vring_ioctl() to prevent a possible use after free as eventfd
could have been released in vhost_vring_ioctl(). And such registering
and unregistering will only be done if DRIVER_OK is set.

## References
- https://git.kernel.org/stable/c/02e9e9366fefe461719da5d173385b6685f70319
- https://git.kernel.org/stable/c/0c170b1e918b9afac25e2bbd01eaa2bfc0ece8c0
- https://git.kernel.org/stable/c/7cf2fb51175cafe01df8c43fa15a06194a59c6e2
- https://git.kernel.org/stable/c/927a2580208e0f9b0b47b08f1c802b7233a7ba3c
- https://git.kernel.org/stable/c/ca64edd7ae93402af2596a952e0d94d545e2b9c0
- https://git.kernel.org/stable/c/ec5f1b54ceb23475049ada6e7a43452cf4df88d1
- https://git.kernel.org/stable/c/fae9b1776f53aab93ab345bdbf653b991aed717d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47748.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
