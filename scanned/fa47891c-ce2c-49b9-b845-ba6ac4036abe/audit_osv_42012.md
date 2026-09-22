# [C] nvmet-auth: validate reply message payload bounds against transfer length

## Summary
Severity: Critical
Advisory: CVE-2026-64319
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64319
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-auth: validate reply message payload bounds against transfer length

nvmet_auth_reply() accesses the variable-length rval[] array using
attacker-controlled hl (hash length) and dhvlen (DH value length) fields
without verifying they fit within the allocated buffer of tl bytes.

A malicious NVMe-oF initiator can craft a DHCHAP_REPLY message with a
small transfer length but large hl/dhvlen values, causing out-of-bounds
heap reads when the target processes the DH public key (rval + 2*hl) or
performs the host response memcmp.

With DH authentication configured, the OOB pointer is passed directly to
sg_init_one() and read by crypto_kpp_compute_shared_secret(), reaching
up to 526 bytes past the buffer. This is exploitable pre-authentication.

Add bounds validation ensuring sizeof(*data) + 2*hl + dhvlen <= tl before
any access to the variable-length fields.

Discovered by Atuin - Automated Vulnerability Discovery Engine.

## References
- https://git.kernel.org/stable/c/3a413ece2504c70aa34a20be4dafec04e8c741f9
- https://git.kernel.org/stable/c/6d7649c1231dac14d906985d2936967e23041c26
- https://git.kernel.org/stable/c/80cd28b56ab62d3e7ed0a7bf05282e6d3ee5b2a0
- https://git.kernel.org/stable/c/999f6205ede984a786f35f727b01f971b98e215d
- https://git.kernel.org/stable/c/caa71b3a43ea5c13fe7141cb019ebcb03b8ac857
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64319.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64319
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
