# [H] Input: cs40l50-vibra - validate custom data from user space

## Summary
Severity: High
Advisory: CVE-2026-80575
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80575
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: cs40l50-vibra - validate custom data from user space

cs40l50_add() copies the custom data of an FF_PERIODIC/FF_CUSTOM effect
straight from the ff_effect the user passed to EVIOCSFF, without
requiring it to hold anything:

    work_data.custom_data = memdup_array_user(periodic->custom_data,
                                              periodic->custom_len,
                                              sizeof(s16));
    work_data.custom_len = periodic->custom_len;

The driver then reads two words out of that buffer: custom_data[0] as the
waveform bank in cs40l50_effect_bank_set(), and custom_data[1] as the
index within the bank in cs40l50_effect_index_set().  Neither read is
covered by a length check, and custom_len is fully user controlled:

  - custom_len == 0 makes memdup_array_user() call memdup_user() with a
    length of zero, which returns ZERO_SIZE_PTR rather than an error, so
    custom_data[0] dereferences it.

  - custom_len == 1 allocates two bytes.  A bank of ROM or RAM keeps
    effect->type out of the OWT case, and custom_data[1] is then read one
    word past the allocation.

The bank value itself is also mishandled.  It is masked with
CS40L50_CUSTOM_DATA_MASK (0xffff) but stored in an s16, so a
custom_data[0] of 0x8000 or above wraps to a negative value that passes
the "bank_type >= CS40L50_WVFRM_BANK_NUM" test.
cs40l50_effect_index_set() indexes vib->dsp.banks[] with it before the
switch statement's default case gets a chance to reject it:

    base_index = vib->dsp.banks[effect->type].base_index;
    max_index = vib->dsp.banks[effect->type].max_index;

Require the two words the driver reads to be present, and hold the masked
bank in a u32 so the existing upper-bound test covers the whole range.
The da7280 haptic driver already range checks custom_len this way.

## References
- https://git.kernel.org/stable/c/3855b6a11f8a7aceb8181cc08c99afef58517006
- https://git.kernel.org/stable/c/52a818c586ae2c36b7324bfaefb547f5e866a8ae
- https://git.kernel.org/stable/c/7d5c576cb1c86047b1fcb1aa9532e17fc5e46c1d
- https://git.kernel.org/stable/c/d38554602a0b04e85fad28ce72c7500cf50d419b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80575.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80575
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
