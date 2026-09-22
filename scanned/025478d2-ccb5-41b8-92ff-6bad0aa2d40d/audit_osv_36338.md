# [H] libceph: reset sparse-read state in osd_fault()

## Summary
Severity: High
Advisory: CVE-2026-23136
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23136
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: reset sparse-read state in osd_fault()

When a fault occurs, the connection is abandoned, reestablished, and any
pending operations are retried. The OSD client tracks the progress of a
sparse-read reply using a separate state machine, largely independent of
the messenger's state.

If a connection is lost mid-payload or the sparse-read state machine
returns an error, the sparse-read state is not reset. The OSD client
will then interpret the beginning of a new reply as the continuation of
the old one. If this makes the sparse-read machinery enter a failure
state, it may never recover, producing loops like:

  libceph:  [0] got 0 extents
  libceph: data len 142248331 != extent len 0
  libceph: osd0 (1)...:6801 socket error on read
  libceph: data len 142248331 != extent len 0
  libceph: osd0 (1)...:6801 socket error on read

Therefore, reset the sparse-read state in osd_fault(), ensuring retries
start from a clean state.

## References
- https://git.kernel.org/stable/c/10b7c72810364226f7b27916ea3e2a4f870bc04b
- https://git.kernel.org/stable/c/11194b416ef95012c2cfe5f546d71af07b639e93
- https://git.kernel.org/stable/c/90a60fe61908afa0eaf7f8fcf1421b9b50e5f7ff
- https://git.kernel.org/stable/c/e94075e950a6598e710b9f7dffea5aa388f40313
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
