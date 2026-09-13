# [C] Fast-DDS Discovery Server: Out-of-Bounds Read & Heap Memory Disclosure via DATA_FRAG  sampleSize / fragmentsInSubmessage

## Summary
Severity: Critical
Advisory: CVE-2026-22590
Aliases: GHSA-7r7h-hwfj-q626
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-22590
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the DDS (Data Distribution Service) standard of the OMG (Object Management Group). Versions prior to 2.6.12, 2.14.6, 3.2.4, 3.3.1, and 3.4.2 have a remotely triggerable Out-of-Bounds Read while processing RTPS `DATA_FRAG` submessages. An attacker can craft a `DATA_FRAG` with a large `sampleSize` but a small actual payload, and set `fragmentsInSubmessage` such that the receiver treats the packet as the LAST fragment**. In this LAST-fragment path, Fast-DDS computes `incoming_length` based on `sampleSize` and calls `memcpy()` without validating `incoming_data.length >= incoming_length`. As a result, `CacheChange_t::add_fragments()` reads past the received UDP datagram buffer and into adjacent heap memory, copying those bytes into the reassembly buffer. In a Discovery Server deployment, the resulting `CacheChange_t` can be relayed to other participants, meaning that a newly joining participant may receive leaked heap memory (e.g., pointer values that could aid ASLR bypass). Versions 2.6.12, 2.14.6, 3.2.4, 3.3.1, and 3.4.2 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22590.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-7r7h-hwfj-q626
- https://nvd.nist.gov/vuln/detail/CVE-2026-22590
