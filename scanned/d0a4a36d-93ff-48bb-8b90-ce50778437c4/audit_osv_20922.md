# [H] CVE-2021-3839

## Summary
Severity: High
Advisory: CVE-2021-3839
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3839
Type: osv

## Details
A flaw was found in the vhost library in DPDK. Function vhost_user_set_inflight_fd() does not validate `msg->payload.inflight.num_queues`, possibly causing out-of-bounds memory read/write. Any software using DPDK vhost library may crash as a result of this vulnerability.

## References
- https://access.redhat.com/security/cve/CVE-2021-3839
- https://bugzilla.redhat.com/show_bug.cgi?id=2025882
- https://github.com/DPDK/dpdk/commit/6442c329b9d2ded0f44b27d2016aaba8ba5844c5
