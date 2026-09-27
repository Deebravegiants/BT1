# [M] drm/amd/display: Add NULL test for 'timing generator' in 'dcn21_set_pipe()'

## Summary
Severity: Medium
Advisory: CVE-2024-26661
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26661
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Add NULL test for 'timing generator' in 'dcn21_set_pipe()'

In "u32 otg_inst = pipe_ctx->stream_res.tg->inst;"
pipe_ctx->stream_res.tg could be NULL, it is relying on the caller to
ensure the tg is not NULL.

## References
- https://git.kernel.org/stable/c/39f24c08363af1cd945abad84e3c87fd3e3c845a
- https://git.kernel.org/stable/c/3f3c237a706580326d3b7a1b97697e5031ca4667
- https://git.kernel.org/stable/c/66951d98d9bf45ba25acf37fe0747253fafdf298
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26661.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26661
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
