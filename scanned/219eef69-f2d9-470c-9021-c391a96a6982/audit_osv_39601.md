# [H] drm/amd/display: Fix out-of-bounds stream encoder index v3

## Summary
Severity: High
Advisory: CVE-2026-46263
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-46263
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix out-of-bounds stream encoder index v3

eng_id can be negative and that stream_enc_regs[]
can be indexed out of bounds.

eng_id is used directly as an index into stream_enc_regs[], which has
only 5 entries. When eng_id is 5 (ENGINE_ID_DIGF) or negative, this can
access memory past the end of the array.

Add a bounds check using ARRAY_SIZE() before using eng_id as an index.
The unsigned cast also rejects negative values.

This avoids out-of-bounds access.

Fixes the below smatch error:
dcn*_resource.c: stream_encoder_create() may index
stream_enc_regs[eng_id] out of bounds (size 5).

drivers/gpu/drm/amd/amdgpu/../display/dc/resource/dcn351/dcn351_resource.c
    1246 static struct stream_encoder *dcn35_stream_encoder_create(
    1247         enum engine_id eng_id,
    1248         struct dc_context *ctx)
    1249 {

    ...

    1255
    1256         /* Mapping of VPG, AFMT, DME register blocks to DIO block instance */
    1257         if (eng_id <= ENGINE_ID_DIGF) {

ENGINE_ID_DIGF is 5.  should <= be <?

Unrelated but, ugh, why is Smatch saying that "eng_id" can be negative?
end_id is type signed long, but there are checks in the caller which prevent it from being negative.

    1258                 vpg_inst = eng_id;
    1259                 afmt_inst = eng_id;
    1260         } else
    1261                 return NULL;
    1262

    ...

    1281
    1282         dcn35_dio_stream_encoder_construct(enc1, ctx, ctx->dc_bios,
    1283                                         eng_id, vpg, afmt,
--> 1284                                         &stream_enc_regs[eng_id],
                                                  ^^^^^^^^^^^^^^^^^^^^^^^ This stream_enc_regs[] array has 5 elements so we are one element beyond the end of the array.

    ...

    1287         return &enc1->base;
    1288 }

v2: use explicit bounds check as suggested by Roman/Dan; avoid unsigned int cast

v3: The compiler already knows how to compare the two values, so the
    cast (int) is not needed. (Roman)

## References
- https://git.kernel.org/stable/c/263e28add4f4472cfa95150d218955d1945aa413
- https://git.kernel.org/stable/c/29f3824b08a98d41ecbbfd33580630d7607f962e
- https://git.kernel.org/stable/c/abde491143e4e12eecc41337910aace4e8d59603
- https://git.kernel.org/stable/c/ca3808d560ad946ab6d089fd1f5bee04b952ead4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46263.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46263
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
