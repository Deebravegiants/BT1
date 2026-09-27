# [H] CVE-2017-1000418

## Summary
Severity: High
Advisory: CVE-2017-1000418
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-02
Source: https://osv.dev/vulnerability/CVE-2017-1000418
Type: osv

## Details
The WildMidi_Open function in WildMIDI since commit d8a466829c67cacbb1700beded25c448d99514e5 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted file.

## References
- https://github.com/Mindwerks/wildmidi/commit/814f31d8eceda8401eb812fc2e94ed143fdad0ab
- https://github.com/Mindwerks/wildmidi/issues/178
