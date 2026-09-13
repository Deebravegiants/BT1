# [H] CVE-2025-56225

## Summary
Severity: High
Advisory: CVE-2025-56225
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-09
Source: https://osv.dev/vulnerability/CVE-2025-56225
Type: osv

## Details
fluidsynth-2.4.6 and earlier versions is vulnerable to Null pointer dereference in fluid_synth_monopoly.c, that can be triggered when loading an invalid midi file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56225.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56225
- https://github.com/FluidSynth/fluidsynth/issues/1602
- https://github.com/FluidSynth/fluidsynth/pull/1607
