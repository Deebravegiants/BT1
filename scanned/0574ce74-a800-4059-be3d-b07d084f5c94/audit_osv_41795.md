# [C] scsi: target: iscsi: Validate CHAP_R length before base64 decode

## Summary
Severity: Critical
Advisory: CVE-2026-63886
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63886
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: iscsi: Validate CHAP_R length before base64 decode

chap_server_compute_hash() allocates client_digest as
kzalloc(chap->digest_size) and then, for BASE64-encoded responses,
passes chap_r directly to chap_base64_decode() without checking whether
the input length could produce more than digest_size bytes of output.

chap_base64_decode() writes to the destination unconditionally as long
as there is input to consume. With MAX_RESPONSE_LENGTH set to 128 and
the "0b" prefix stripped by extract_param(), up to 127 base64 characters
can reach the decoder. 127 characters decode to 95 bytes. For SHA-256
(digest_size=32) this overflows client_digest by 63 bytes; for MD5
(digest_size=16) the overflow is 79 bytes.

The length check at line 344 fires after the write has already happened.

The HEX branch in the same switch statement already validates the length
up front. Apply the same approach to the BASE64 branch: strip trailing
base64 padding characters, then reject any input whose data length
exceeds DIV_ROUND_UP(digest_size * 4, 3) before calling the decoder.

Stripping trailing '=' before the comparison handles both padded and
unpadded encodings. chap_base64_decode() already returns early on '=',
so the full original string is still passed to the decoder unchanged.

The mutual CHAP path decodes CHAP_C into initiatorchg_binhex, which is
kzalloc(CHAP_CHALLENGE_STR_LEN). extract_param() caps initiatorchg at
CHAP_CHALLENGE_STR_LEN characters, so at most CHAP_CHALLENGE_STR_LEN-1
base64 characters reach the decoder. The maximum decoded size,
DIV_ROUND_UP((CHAP_CHALLENGE_STR_LEN-1) * 3, 4), is less than
CHAP_CHALLENGE_STR_LEN, so no overflow is possible there. A comment is
added at the call site to document this.

## References
- https://git.kernel.org/stable/c/4a3a19c98a8207ad08bec554703d90f2c34a8cc6
- https://git.kernel.org/stable/c/82454e6f21e56ea9a0a9de7d0ff7e1dfb83e34d6
- https://git.kernel.org/stable/c/85db7391310b1304d2dc8ae3b0b12105a9567147
- https://git.kernel.org/stable/c/bf154c657828ed05399bca5d98cf1611bb048b12
- https://git.kernel.org/stable/c/c04e85799356120209b351a148ac2db888d5ffd9
- https://git.kernel.org/stable/c/edd06675a02376ea8347dba7c29ad982ba5b36ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63886.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63886
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
