# [H] ksmbd: validate NTLMv2 response before updating session key

## Summary
Severity: High
Advisory: CVE-2026-64389
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64389
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.18.40, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate NTLMv2 response before updating session key

ksmbd_auth_ntlmv2() derives the NTLMv2 session key into
sess->sess_key before it verifies the NTLMv2 response.
ksmbd_decode_ntlmssp_auth_blob() then continues into KEY_XCH even
when ksmbd_auth_ntlmv2() failed.

With SMB3 multichannel binding, the failed authentication operates on
an existing session and the session setup error path does not expire
binding sessions. A client can send a binding session setup with a
bad NT proof and KEY_XCH and still modify sess->sess_key before
STATUS_LOGON_FAILURE is returned.

Relevant path:

  smb2_sess_setup()
    -> conn->binding = true
    -> ntlm_authenticate()
       -> session_user()
       -> ksmbd_decode_ntlmssp_auth_blob()
          -> ksmbd_auth_ntlmv2()
             -> calc_ntlmv2_hash()
             -> hmac_md5_usingrawkey(..., sess->sess_key)
             -> crypto_memneq() returns mismatch
          -> KEY_XCH arc4_crypt(..., sess->sess_key, ...)
    -> out_err without expiring the binding session

Derive the base session key into a local buffer and copy it to
sess->sess_key only after the proof matches. Return immediately on
authentication failure so KEY_XCH is only processed after successful
authentication.

## References
- https://git.kernel.org/stable/c/89ca7756d5566ba636bb9092cdbe57dab095e136
- https://git.kernel.org/stable/c/954d196bebb2b50151cb96454c72dc113b2af1ac
- https://git.kernel.org/stable/c/b56400364aed5c34d6e1a0b493081290a5328a9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64389.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
