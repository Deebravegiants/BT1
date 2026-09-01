# [M] CVE-2026-8925: SASL double-free

## Summary
Severity: Medium
Program: curl
Weakness: Double Free
Reporter: giant_anteater
State: resolved
Disclosed: 2026-06-24T08:23:35.633Z
CVE: CVE-2026-8925
Source: https://hackerone.com/reports/3735193

## Details
Hi all,

We found a double-free in the GSASL authentication path — `Curl_auth_gsasl_is_supported()` frees `gsasl->ctx` on a failed `gsasl_client_start()` but never nulls the pointer, and then `Curl_auth_gsasl_cleanup()` frees it again unconditionally at connection teardown.

The bug lives in two spots. `lib/vauth/gsasl.c:47-50`:

```c
res = gsasl_client_start(gsasl->ctx, mech, &gsasl->client);
if(res != GSASL_OK) {
  gsasl_done(gsasl->ctx);   /* frees gsasl->ctx ... */
  return FALSE;              /* ... but gsasl->ctx still holds the freed pointer */
}
```

And the cleanup function at `lib/vauth/gsasl.c:108-115`:

```c
void Curl_auth_gsasl_cleanup(struct gsasldata *gsasl)
{
  gsasl_finish(gsasl->client);
  gsasl->client = NULL;

  gsasl_done(gsasl->ctx);   /* no NULL guard — second free if probe failed */
  gsasl->ctx = NULL;
}
```

`Curl_auth_gsasl_cleanup()` is called unconditionally at connection close via `gsasl_conn_dtor` at `lib/vauth/vauth.c:201-209`. What makes this land reliably is that `sasl_choose_gsasl()` in `lib/curl_sasl.c:354-383` allocates a single `struct gsasldata` for the connection and passes the same pointer to each mechanism probe:

```c
gsasl = Curl_auth_gsasl_get(sctx->conn);   /* one struct, reused across all probes */

if((sctx->enabledmechs & SASL_MECH_SCRAM_SHA_256) &&
   Curl_auth_gsasl_is_supported(data, SASL_MECH_STRING_SCRAM_SHA_256, gsasl)) {
  ...
}
else if((sctx->enabledmechs & SASL_MECH_SCRAM_SHA_1) &&
        Curl_auth_gsasl_is_supported(data, SASL_MECH_STRING_SCRAM_SHA_1, gsasl)) {
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3735193_
