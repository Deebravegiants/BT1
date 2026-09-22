# [H] scsi: scsi_transport_fc: Widen FPIN pname walker counter to u32

## Summary
Severity: High
Advisory: CVE-2026-63889
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63889
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: scsi_transport_fc: Widen FPIN pname walker counter to u32

An adjacent Fibre Channel fabric actor that can deliver an FPIN ELS
frame to an lpfc or qla2xxx Linux initiator can trigger a non-return in
the generic FC transport. This is not a local userspace or IP network
path; the attacker must be able to inject fabric traffic, for example as
a compromised switch or fabric controller, or as a same-zone N_Port on a
fabric that permits source spoofing.

The Link-Integrity and Peer-Congestion FPIN walkers used a u8 loop
counter against the 32-bit on-wire pname_count field, and did not bound
pname_count by the descriptor body already validated by the TLV walker.
A pname_count of 256 therefore wraps the counter and keeps the loop
condition true indefinitely.

Factor the shared pname_list[] walk into one helper, widen the counter
to u32, and clamp pname_count against the entries that fit in the
descriptor body before iterating.

## References
- https://git.kernel.org/stable/c/07776b7779c9426982c1ad74aad91bd531593790
- https://git.kernel.org/stable/c/163bd704d7515c3df6c2e03bcba93d1db79edbff
- https://git.kernel.org/stable/c/29f126f09e34a425b376b3646c89aa7cc18b142c
- https://git.kernel.org/stable/c/35461d23744175a78b6280293892cca357c22793
- https://git.kernel.org/stable/c/a9a39233ec1fc9f97ea1340a4d09bb7ec2be5153
- https://git.kernel.org/stable/c/bdff76dff6ec23d6fe35812fa33e5c4ce2cdb770
- https://git.kernel.org/stable/c/ee57b89e5da9fffbe0d26647e4ff0750dacb9943
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63889.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63889
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
