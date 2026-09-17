# [M] CVE-2021-21417

## Summary
Severity: Medium
Advisory: CVE-2021-21417
Aliases: GHSA-6fcq-pxhc-jxc9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-21417
Type: osv

## Details
fluidsynth is a software synthesizer based on the SoundFont 2 specifications. A use after free violation was discovered in fluidsynth, that can be triggered when loading an invalid SoundFont file.

## References
- https://github.com/FluidSynth/fluidsynth/security/advisories/GHSA-6fcq-pxhc-jxc9
- https://lists.debian.org/debian-lts-announce/2021/06/msg00027.html
- https://github.com/FluidSynth/fluidsynth/pull/810
- https://github.com/FluidSynth/fluidsynth/issues/808
