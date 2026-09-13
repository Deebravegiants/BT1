# [H] ALSA: aloop: Fix peer runtime UAF during format-change stop

## Summary
Severity: High
Advisory: CVE-2026-46090
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46090
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.12.88, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: aloop: Fix peer runtime UAF during format-change stop

loopback_check_format() may stop the capture side when playback starts
with parameters that no longer match a running capture stream. Commit
826af7fa62e3 ("ALSA: aloop: Fix racy access at PCM trigger") moved
the peer lookup under cable->lock, but the actual snd_pcm_stop() still
runs after dropping that lock.

A concurrent close can clear the capture entry from cable->streams[] and
detach or free its runtime while the playback trigger path still holds a
stale peer substream pointer.

Keep a per-cable count of in-flight peer stops before dropping
cable->lock, and make free_cable() wait for those stops before
detaching the runtime. This preserves the existing behavior while
making the peer runtime lifetime explicit.

## References
- https://git.kernel.org/stable/c/03f52a9c170431e8f10e156b9dc0dae80b3e9198
- https://git.kernel.org/stable/c/345c24b2bcf0923dfae1ab41497351c68214ff76
- https://git.kernel.org/stable/c/5d45e34bf001344e2966dabca1897561bbc9e913
- https://git.kernel.org/stable/c/83bd62fa9620ac98d5d694bde14c50f98c8e7189
- https://git.kernel.org/stable/c/bdd9503c3d222d2735b56c7a8b4422ccf3de6e5c
- https://git.kernel.org/stable/c/e5c33cdc6f402eab8abd36ecf436b22c9d3a8aff
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46090.json
- https://access.redhat.com/errata/RHSA-2026:27353
- https://access.redhat.com/errata/RHSA-2026:27354
- https://access.redhat.com/errata/RHSA-2026:30848
- https://access.redhat.com/errata/RHSA-2026:33215
- https://access.redhat.com/errata/RHSA-2026:33685
- https://access.redhat.com/errata/RHSA-2026:33899
- https://access.redhat.com/errata/RHSA-2026:33900
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:34095
- https://access.redhat.com/errata/RHSA-2026:34443
- https://access.redhat.com/errata/RHSA-2026:35844
- https://access.redhat.com/errata/RHSA-2026:35863
- https://access.redhat.com/errata/RHSA-2026:35896
