# [H] ksmbd: validate response sizes in ipc_validate_msg()

## Summary
Severity: High
Advisory: CVE-2026-31707
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31707
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.141, >=6.7.0 <6.12.84, >=6.13.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate response sizes in ipc_validate_msg()

ipc_validate_msg() computes the expected message size for each
response type by adding (or multiplying) attacker-controlled fields
from the daemon response to a fixed struct size in unsigned int
arithmetic.  Three cases can overflow:

  KSMBD_EVENT_RPC_REQUEST:
      msg_sz = sizeof(struct ksmbd_rpc_command) + resp->payload_sz;
  KSMBD_EVENT_SHARE_CONFIG_REQUEST:
      msg_sz = sizeof(struct ksmbd_share_config_response) +
               resp->payload_sz;
  KSMBD_EVENT_LOGIN_REQUEST_EXT:
      msg_sz = sizeof(struct ksmbd_login_response_ext) +
               resp->ngroups * sizeof(gid_t);

resp->payload_sz is __u32 and resp->ngroups is __s32.  Each addition
can wrap in unsigned int; the multiplication by sizeof(gid_t) mixes
signed and size_t, so a negative ngroups is converted to SIZE_MAX
before the multiply.  A wrapped value of msg_sz that happens to
equal entry->msg_sz bypasses the size check on the next line, and
downstream consumers (smb2pdu.c:6742 memcpy using rpc_resp->payload_sz,
kmemdup in ksmbd_alloc_user using resp_ext->ngroups) then trust the
unverified length.

Use check_add_overflow() on the RPC_REQUEST and SHARE_CONFIG_REQUEST
paths to detect integer overflow without constraining functional
payload size; userspace ksmbd-tools grows NDR responses in 4096-byte
chunks for calls like NetShareEnumAll, so a hard transport cap is
unworkable on the response side.  For LOGIN_REQUEST_EXT, reject
resp->ngroups outside the signed [0, NGROUPS_MAX] range up front and
report the error from ipc_validate_msg() so it fires at the IPC
boundary; with that bound the subsequent multiplication and addition
stay well below UINT_MAX.  The now-redundant ngroups check and
pr_err in ksmbd_alloc_user() are removed.

This is the response-side analogue of aab98e2dbd64 ("ksmbd: fix
integer overflows on 32 bit systems"), which hardened the request
side.

## References
- https://git.kernel.org/stable/c/299db777ea0cfa5c407e41b045c24a14c034c27b
- https://git.kernel.org/stable/c/7dd0c858e1909769a4c91842724315ee74f1a5f1
- https://git.kernel.org/stable/c/99c631d0366c1eab8fb188fe66425f4581ebdde4
- https://git.kernel.org/stable/c/bf396208418371174869baba9434535cd3288e80
- https://git.kernel.org/stable/c/d6a6aa81eac2c9bff66dc6e191179cb69a14426b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31707.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31707
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
