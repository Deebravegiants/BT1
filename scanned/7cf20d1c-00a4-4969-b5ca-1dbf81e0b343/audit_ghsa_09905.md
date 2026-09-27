# [H] Zserio Runtime: Integer Overflow in BitStreamReader and Unbounded Memory Allocation in Deserialization

## Summary
Severity: High
Advisory: GHSA-cwq5-8pvq-j65j
CVE: CVE-2026-33524
CWE: CWE-789
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-cwq5-8pvq-j65j
Type: github-advisory

## Affected
- Maven: `io.github.ndsev:zserio-runtime` — affected >=0 <2.18.1

## Details
## Summary

### Unbounded Memory Allocation (all platforms)

A crafted payload as small as 4-5 bytes can force memory allocations of up to 16 GB, crashing any process with an OOM error (Denial of Service).

**Affected code (C++):**
- `cpp/runtime/src/zserio/Array.h` (line 1029) — `m_rawArray.reserve(readLength)` with unchecked `readLength`
- `cpp/runtime/src/zserio/BitStreamReader.h` (lines 249, 281) — `value.reserve(len)` with unchecked `len`

**Affected code (Java):**
- `java/runtime/src/zserio/runtime/array/Array.java` (line 271) — `rawArray.reset(readSize)` → `new int[readSize]`
- `java/runtime/src/zserio/runtime/io/ByteArrayBitStreamReader.java` (line 245) — `new byte[length]`

## Proof of Concept

### Memory Allocation DoS (verified on 64-bit)

| Payload | Claimed Size | Allocated | Amplification |
|---------|-------------|-----------|---------------|
| 4 bytes | 100,000,000 | 762 MB | ~200 million x |
| 5 bytes | 2,147,483,647 | ~16 GB | system crash |

The full PoC source code and Docker build files are available upon request.

## Impact

zserio is the serialization framework underlying the **NDS (Navigation Data Standard)**, used by 43 member companies including Toyota, BMW, Volkswagen, Mercedes-Benz, and others. According to the Eclipse zserio project:

> "Zserio serialized data is used in millions of deployments in cars on the road"

Attack vectors include NDS.Live cloud map updates, map data supply chain compromise, and backend data processing pipelines. On 32-bit automotive ECUs, this could affect ADAS functionality.

## Suggested Fix

### For all runtimes: Validate varsize against stream size

```
if (claimedSize > remainingBytesInStream) {
    throw error("varsize claims more data than available in stream");
}
```

## Disclosure Timeline

- **2026-03-08:** Reported to Woven by Toyota PSIRT (go-zserio)
- **2026-03-10:** Reported to ndsev/zserio maintainers via GitHub Security Advisory
- **2026-03-23:** Split off overflow vulnerability to own report
- **90-day coordinated disclosure timeline**

A patch for this issue is available at https://github.com/ndsev/zserio/releases/tag/v2.18.1.

## Reporter

Ryuji Yasukochi (ryuji.yasu@gmail.com)

## References
- https://github.com/ndsev/zserio/security/advisories/GHSA-cwq5-8pvq-j65j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33524
- https://github.com/ndsev/zserio/commit/a9932de4b5eefb3afd5e18ca2fd758aa744a7c69
- https://github.com/ndsev/zserio
