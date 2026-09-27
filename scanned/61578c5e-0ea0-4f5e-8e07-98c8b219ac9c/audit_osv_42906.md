# [C] nvmet-auth: reject short AUTH_RECEIVE buffers

## Summary
Severity: Critical
Advisory: CVE-2026-72130
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72130
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.101, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-auth: reject short AUTH_RECEIVE buffers

nvmet_execute_auth_receive() trusts the AUTH_RECEIVE allocation length
after checking only that it is nonzero and matches the transfer length.
In the SUCCESS1 and FAILURE1/default states, that lets a remote NVMe-oF
initiator reach the fixed-size DH-HMAC-CHAP response builders with a
kmalloc() buffer shorter than the response, so nvmet_auth_success1() and
nvmet_auth_failure1() write past the allocation; both only WARN_ON the
short length and then format the message anyway.

Impact: A remote NVMe-oF initiator with access to an auth-enabled target
can trigger a 16-byte heap out-of-bounds write via a one-byte
AUTH_RECEIVE allocation length.

Compute the minimum response length for the current DH-HMAC-CHAP step in
nvmet_auth_receive_data_len() and report a zero data length when the
host-supplied allocation length is shorter, so the existing zero-length
check in nvmet_execute_auth_receive() rejects the command before any
builder runs. The SUCCESS1 minimum is sizeof(struct
nvmf_auth_dhchap_success1_data) plus the HMAC hash length, because the
response hash is written into the rval[] flexible-array tail, so the
minimum is state dependent rather than a flat sizeof. CHALLENGE keeps its
existing variable-length guard in nvmet_auth_challenge().

This is reachable only when in-band DH-HMAC-CHAP authentication is
configured on the target.

## References
- https://git.kernel.org/stable/c/2eaa3ad450141cfcf187bb43cb8335eb336b5f87
- https://git.kernel.org/stable/c/779575bc35c687697ba69e904f2cd22e60112534
- https://git.kernel.org/stable/c/80bf7b7f676e3987bbe06af3c359bd56ac91a5a9
- https://git.kernel.org/stable/c/bc111698b46e43eddd8664cceaa621cd559e99a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72130.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72130
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
