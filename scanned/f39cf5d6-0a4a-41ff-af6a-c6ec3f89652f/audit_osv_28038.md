# [M] drm/amd/display: Add 'replay' NULL check in 'edp_set_replay_allow_active()'

## Summary
Severity: Medium
Advisory: CVE-2024-27040
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27040
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Add 'replay' NULL check in 'edp_set_replay_allow_active()'

In the first if statement, we're checking if 'replay' is NULL. But in
the second if statement, we're not checking if 'replay' is NULL again
before calling replay->funcs->replay_set_power_opt().

if (replay == NULL && force_static)
    return false;

...

if (link->replay_settings.replay_feature_enabled &&
    replay->funcs->replay_set_power_opt) {
	replay->funcs->replay_set_power_opt(replay, *power_opts, panel_inst);
	link->replay_settings.replay_power_opt_active = *power_opts;
}

If 'replay' is NULL, this will cause a null pointer dereference.

Fixes the below found by smatch:
drivers/gpu/drm/amd/amdgpu/../display/dc/link/protocols/link_edp_panel_control.c:895 edp_set_replay_allow_active() error: we previously assumed 'replay' could be null (see line 887)

## References
- https://git.kernel.org/stable/c/d0e94f4807ff0df66cf447d6b4bbb8ac830e99c3
- https://git.kernel.org/stable/c/e7cadd5d3a8ffe334d0229ba9eda4290138d56e7
- https://git.kernel.org/stable/c/f610c46771ef1047e46d61807aa7c69cd29e63d8
- https://git.kernel.org/stable/c/f6aed043ee5d75b3d1bfc452b1a9584b63c8f76b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27040.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27040
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
