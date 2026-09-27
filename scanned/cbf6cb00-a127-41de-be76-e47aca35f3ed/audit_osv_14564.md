# [M] CVE-2019-1010317

## Summary
Severity: Medium
Advisory: CVE-2019-1010317
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-1010317
Type: osv

## Details
WavPack 5.1.0 and earlier is affected by: CWE-457: Use of Uninitialized Variable. The impact is: Unexpected control flow, crashes, and segfaults. The component is: ParseCaffHeaderConfig (caff.c:486). The attack vector is: Maliciously crafted .wav file. The fixed version is: After commit https://github.com/dbry/WavPack/commit/f68a9555b548306c5b1ee45199ccdc4a16a6101b.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CFFFWIWALGQPKINRDW3PRGRD5LOLGZA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BRWQNE3TH5UF64IKHKKHVCHJHUOVKJUH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IX3J2JML5A7KC2BLGBEFTIIZR3EM7LVJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PYESOAZ6Z6IG4BQBURL6OUY6P4YB6SKS/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00013.html
- https://usn.ubuntu.com/4062-1/
- https://github.com/dbry/WavPack/issues/66
- https://github.com/dbry/WavPack/commit/f68a9555b548306c5b1ee45199ccdc4a16a6101b
