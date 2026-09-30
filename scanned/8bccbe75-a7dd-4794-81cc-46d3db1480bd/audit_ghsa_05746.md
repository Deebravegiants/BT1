# [H] Incus container environment configuration newline injection

## Summary
Severity: High
Advisory: GHSA-x6jc-phwx-hp32
CVE: CVE-2026-23953
CWE: CWE-93
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-x6jc-phwx-hp32
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6` — affected >=0 <6.21.0

## Details
### Summary
A user with the ability to launch a container with a custom YAML configuration (e.g a member of the ‘incus’ group) can create an environment variable containing newlines, which can be used to add additional configuration items in the container’s `lxc.conf` due to the newline injection. This can allow adding arbitrary lifecycle hooks, ultimately resulting in arbitrary command execution on the host.

### Details
When passing environment variables in the config block of a new container, values are not checked for the presence of newlines [1], which can result in newline injection inside the generated container `lxc.conf`. This can be used to set arbitrary additional configuration items, such as `lxc.hook.pre-start`. By exploiting this, a user with the ability to launch a container with an arbitrary config can achieve arbitrary command execution as root on the host.

Exploiting this issue on IncusOS requires a slight modification of the payload to change to a different writable directory for the validation step (e.g /tmp). This can be confirmed with a second container with /tmp mounted from the host (A privileged action for validation only).

[1] https://github.com/lxc/incus/blob/HEAD/internal/server/instance/drivers/driver_lxc.go#L1081

### PoC
A proof-of-concept script exploiting this vulnerability can be found attached, named environment_newline_injection.sh, showing arbitrary command execution, which will write a file to the root filesystem (`/newline_injection_command_exec_poc`)

Manual Reproduction steps:
1. Launch a new container with a configuration file containing a multiline YAML string as an environment variable value, such as in the listing below.
2. Observe that the lxc.conf (`/run/incus/user-1000_poc/lxc.conf` in my case) contains an additional `lxc.hook.pre-start` item
3. Observe the creation of the file in the host root directory, with contents proving command execution as root.

```
incus launch images:alpine/edge --ephemeral poc << EOF
config:
  environment.FOO: |-
    abc
    lxc.hook.pre-start = /bin/sh -c "id > /newline_injection_command_exec_poc"
EOF
```

### Impact
A user with the ability to launch a container with a custom YAML configuration (e.g a member of the ‘incus’ group) can achieve arbitrary command execution on the host.

### Attachments
[environment_newline_injection.sh](https://github.com/user-attachments/files/24473682/environment_newline_injection.sh)
[environment_newline_injection.patch](https://github.com/user-attachments/files/24473685/environment_newline_injection.patch)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-x6jc-phwx-hp32
- https://nvd.nist.gov/vuln/detail/CVE-2026-23953
- https://github.com/lxc/incus
- https://github.com/lxc/incus/blob/HEAD/internal/server/instance/drivers/driver_lxc.go#L1081
- https://github.com/user-attachments/files/24473682/environment_newline_injection.sh
- https://github.com/user-attachments/files/24473685/environment_newline_injection.patch
