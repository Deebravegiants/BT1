# [H] s390/zcrypt: Improve EP11 CPRB domain handling with ASN.1 parsing

## Summary
Severity: High
Advisory: CVE-2026-80544
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80544
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/zcrypt: Improve EP11 CPRB domain handling with ASN.1 parsing

The zcrypt_msgtype6_send_ep11_cprb() function uses fragile struct
overlays to access and modify the domain field in the EP11 CPRB
payload, creating maintainability and security concerns:
1. Struct overlay approach (pld_hdr) assumes fixed payload structure
   and doesn't validate the actual ASN.1 encoding.
2. Complex length format detection logic is error-prone and doesn't
   properly validate bounds at each parsing step.
3. Direct struct member access bypasses proper ASN.1 validation.

Fix by replacing struct overlays with explicit ASN.1 parsing that
validates each field (payload tag/length, function tag/length/value,
optional domain tag/length/value) with proper bounds checking at every
step. Add asn1_int_encode() helper function to safely write integer
values with correct endianness conversion. This makes the code
consistent with the validation pattern introduced with the rework of
the xcrb_msg_to_type6_ep11cprb_msgx() function.

## References
- https://git.kernel.org/stable/c/0864a163783bff109b548266921829ea794edc93
- https://git.kernel.org/stable/c/db21b2cf6dd0af5ffd08931e0a9fcda5a0473220
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80544.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80544
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
