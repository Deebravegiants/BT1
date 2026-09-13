# [H] s390/zcrypt: Improve EP11 CPRB length and overflow checks

## Summary
Severity: High
Advisory: CVE-2026-80545
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80545
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/zcrypt: Improve EP11 CPRB length and overflow checks

The xcrb_msg_to_type6_ep11cprb_msgx() function lacks proper input
validation, creating security vulnerabilities:
1. Missing minimum size validation: The ep11_cprb structure and
   subsequent payload fields (pld_tag, pld_lenfmt) are copied from
   userspace without verifying sufficient buffer length.
2. Arithmetic overflow in length calculations: CEIL4 alignment could
   overflow, bypassing size checks and enabling buffer overflows.
3. The payload is asn1 encoded but the function just uses a simple c
   struct overlay to access some fields of the payload.

Fix by using size_t for length calculations, adding U32_MAX boundary
checks after alignment, and validating minimum request size and
minimum reply size before copying from userspace. Do a very simple
asn1 parsing of the payload up to the function value field.

## References
- https://git.kernel.org/stable/c/17ac0bc866fc624cd05f022dcd8b730c0af11bb1
- https://git.kernel.org/stable/c/2976b9d2e716c7e5487ca7c29a7bd076cf9adf08
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80545.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80545
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
