# [C] CVE-2018-19333

## Summary
Severity: Critical
Advisory: CVE-2018-19333
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-17
Source: https://osv.dev/vulnerability/CVE-2018-19333
Type: osv

## Details
pkg/sentry/kernel/shm/shm.go in Google gVisor before 2018-11-01 allows attackers to overwrite memory locations in processes running as root (but not escape the sandbox) via vectors involving IPC_RMID shmctl calls, because reference counting is mishandled.

## References
- https://github.com/google/gvisor/commit/0e277a39c8b6f905e289b75e8ad0594e6b3562ca
- https://justi.cz/security/2018/11/14/gvisor-lpe.html
