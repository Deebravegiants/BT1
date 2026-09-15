# [M] CVE-2018-20699

## Summary
Severity: Medium
Advisory: CVE-2018-20699
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-12
Source: https://osv.dev/vulnerability/CVE-2018-20699
Type: osv

## Details
Docker Engine before 18.09 allows attackers to cause a denial of service (dockerd memory consumption) via a large integer in a --cpuset-mems or --cpuset-cpus value, related to daemon/daemon_unix.go, pkg/parsers/parsers.go, and pkg/sysinfo/sysinfo.go.

## References
- https://access.redhat.com/errata/RHSA-2019:0487
- https://github.com/docker/engine/pull/70
- https://github.com/moby/moby/pull/37967
