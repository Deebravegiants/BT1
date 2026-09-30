# [H] drm/amd/display: Implement bounds check for stream encoder creation in DCN301

## Summary
Severity: High
Advisory: CVE-2024-26660
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26660
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.149, >=5.16.0 <6.1.78, >=6.2.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Implement bounds check for stream encoder creation in DCN301

'stream_enc_regs' array is an array of dcn10_stream_enc_registers
structures. The array is initialized with four elements, corresponding
to the four calls to stream_enc_regs() in the array initializer. This
means that valid indices for this array are 0, 1, 2, and 3.

The error message 'stream_enc_regs' 4 <= 5 below, is indicating that
there is an attempt to access this array with an index of 5, which is
out of bounds. This could lead to undefined behavior

Here, eng_id is used as an index to access the stream_enc_regs array. If
eng_id is 5, this would result in an out-of-bounds access on the
stream_enc_regs array.

Thus fixing Buffer overflow error in dcn301_stream_encoder_create
reported by Smatch:
drivers/gpu/drm/amd/amdgpu/../display/dc/resource/dcn301/dcn301_resource.c:1011 dcn301_stream_encoder_create() error: buffer overflow 'stream_enc_regs' 4 <= 5

## References
- https://git.kernel.org/stable/c/42442f74314d41ddc68227047036fa3e78940054
- https://git.kernel.org/stable/c/58fca355ad37dcb5f785d9095db5f748b79c5dc2
- https://git.kernel.org/stable/c/a938eab9586eea31cfd129a507f552efae14d738
- https://git.kernel.org/stable/c/cd9bd10c59e3c1446680514fd3097c5b00d3712d
- https://git.kernel.org/stable/c/efdd665ce1a1634b8c1dad5e7f6baaef3e131d0a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26660.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26660
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
