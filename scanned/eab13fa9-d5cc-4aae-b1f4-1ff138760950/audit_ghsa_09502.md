# [H] Apache OpenNLP AbstractModelReader has an OOM Denial of Service via Unbounded Array Allocation

## Summary
Severity: High
Advisory: GHSA-659w-93r5-9j6m
CVE: CVE-2026-42440
CWE: CWE-789
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-659w-93r5-9j6m
Type: github-advisory

## Affected
- Maven: `org.apache.opennlp:opennlp-tools` — affected >=0 <2.5.9
- Maven: `org.apache.opennlp:opennlp-tools` — affected >=3.0.0-M1 <3.0.0-M3

## Details
OOM Denial of Service via Unbounded Array Allocation in Apache OpenNLP AbstractModelReader 

Versions Affected: 

Before 2.5.9

Before 3.0.0-M3 

Description:


The AbstractModelReader methods getOutcomes(), getOutcomePatterns(), and getPredicates() each read a 32-bit signed integer count field from a binary model stream and pass that value directly to an array allocation (new String[numOutcomes], new int[numOCTypes][], new String[NUM_PREDS]) without validating that the value is non-negative or within a reasonable bound. The count is therefore fully attacker-controlled when the model file originates from an untrusted source.


A crafted .bin model file in which any of these count fields is set to Integer.MAX_VALUE (or any value large enough to exhaust the available heap) triggers an OutOfMemoryError at the array allocation itself, before the corresponding label or pattern data is consumed from the stream. The error occurs very early in deserialization: for a GIS model, getOutcomes() is reached after only the model-type string, the correction constant, and the correction parameter have been read; so the attacker pays no meaningful size cost to weaponize a payload, and a single small file can crash a JVM that loads it. Any code path that deserializes a .bin model is affected, including direct use of GenericModelReader and any higher-level component that delegates to it during model load.


The practical impact is denial of service against processes that load model files from untrusted or semi-trusted origins.  


Mitigation:



  *  2.x users should upgrade to 2.5.9.

  *  3.x users should upgrade to 3.0.0-M3.




Note: The fix introduces an upper bound on each of the three count fields, checked before array allocation; counts that are negative or exceed the bound cause an IllegalArgumentException to be thrown and the read to fail fast with no large allocation. The default bound is 10,000,000, which is well above the entry counts of legitimate OpenNLP models but far below any value that would threaten heap exhaustion. Deployments that legitimately need to load models with more entries than the default can raise the limit at JVM startup by setting the OPENNLP_MAX_ENTRIES system property to the desired positive integer (e.g. -DOPENNLP_MAX_ENTRIES=50000000); invalid or non-positive values fall back to the default.


Users who cannot upgrade immediately should treat all .bin model files as untrusted input unless their provenance is verified, and should avoid loading models supplied by end users or fetched from third-party repositories without integrity checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42440
- https://github.com/apache/opennlp
- https://lists.apache.org/thread/s8xlkx1gqbxfsq48py5h6jphjvgqp1jo
- http://www.openwall.com/lists/oss-security/2026/05/01/21
