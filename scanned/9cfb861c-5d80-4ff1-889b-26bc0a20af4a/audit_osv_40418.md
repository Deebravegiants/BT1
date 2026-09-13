# [C] IB/isert: Reject login PDUs shorter than ISER_HEADERS_LEN

## Summary
Severity: Critical
Advisory: CVE-2026-53176
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53176
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/isert: Reject login PDUs shorter than ISER_HEADERS_LEN

In drivers/infiniband/ulp/isert/ib_isert.c, isert_login_recv_done()
computes the login request payload length as wc->byte_len minus
ISER_HEADERS_LEN with no lower bound, and login_req_len is a signed int.
A remote iSER initiator can post a login Send work request carrying
fewer than ISER_HEADERS_LEN (76) bytes, so the subtraction underflows
and login_req_len becomes negative.

isert_rx_login_req() then reads that negative length back into a signed
int, takes size = min(rx_buflen, MAX_KEY_VALUE_PAIRS), and because the
min() is signed it keeps the negative value; the value is then passed as
the memcpy() length and sign-extended to a multi-gigabyte size_t. The
copy into the 8192-byte login->req_buf runs far out of bounds and
faults, crashing the target node. The login phase precedes iSCSI
authentication, so no credentials are required to reach this path.

Reject any login PDU shorter than ISER_HEADERS_LEN before the
subtraction, mirroring the existing early return on a failed work
completion, so login_req_len can never go negative. The upper bound was
already safe: a posted login buffer cannot deliver more than
ISER_RX_PAYLOAD_SIZE, so the difference stays at or below
MAX_KEY_VALUE_PAIRS and the existing min() clamps it; only the missing
lower bound needs to be added.

## References
- https://git.kernel.org/stable/c/1ca40b243277c9e88be5e00bd3e083f71aefb93e
- https://git.kernel.org/stable/c/29e7b925ae6df64894e82ab6419994dc25580a8a
- https://git.kernel.org/stable/c/75ee6e4aa096aa9e7b2dd5c8ff98356e30aceefb
- https://git.kernel.org/stable/c/bd22740d7f14cb1c0289444cfd2c8d2938667c1d
- https://git.kernel.org/stable/c/c1234229399f4af12c553b1b0ffd978eeba65548
- https://git.kernel.org/stable/c/c5584e089b5af7b3bf8bd5e8ca0560cbf32b0a47
- https://git.kernel.org/stable/c/df422fd273c96c2ee5beb80fc21adc8c70c29260
- https://git.kernel.org/stable/c/e8a013c0c3ca2f6708341a56612a3f6d6921620a
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53176.json
- https://access.redhat.com/security/cve/CVE-2026-53176
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53176.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53176
- https://bugzilla.redhat.com/show_bug.cgi?id=2492741
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
