# [H] tpm: tpm2-sessions: wait for async KPP completion in tpm_buf_append_salt

## Summary
Severity: High
Advisory: CVE-2026-72151
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72151
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tpm: tpm2-sessions: wait for async KPP completion in tpm_buf_append_salt

tpm_buf_append_salt() in drivers/char/tpm/tpm2-sessions.c calls
crypto_kpp_generate_public_key() and crypto_kpp_compute_shared_secret()
without installing a completion callback, discards both return values,
and immediately frees the kpp_request via kpp_request_free(). When the
resolved ecdh-nist-p256 KPP backend is asynchronous (atmel-ecc, HPRE,
keembay-ocs), either operation returns -EINPROGRESS and the deferred
completion worker dereferences the freed request.

The path fires automatically from the hwrng_fillfn kernel thread via
tpm_get_random -> tpm2_get_random -> tpm2_start_auth_session ->
tpm_buf_append_salt on every entropy poll, without any userland action.

Install crypto_req_done as the completion callback, wrap both KPP
operations in crypto_wait_req(), and propagate errors to the caller.
The wait is a no-op for synchronous backends.

## References
- https://git.kernel.org/stable/c/111e520efbe82b324bc42b1999b723c0619eea6d
- https://git.kernel.org/stable/c/493333f167926c7adab8e7563e21ad71d8af84fa
- https://git.kernel.org/stable/c/73851a7c43dfa52d2ed9415889b33daf85da0ed9
- https://git.kernel.org/stable/c/934d1cd40e2893bf7a041b54f6afd1c008d7a21c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72151.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72151
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
