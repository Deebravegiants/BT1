# [H] Reading specially crafted serializable objects from an untrusted source may cause an infinite loop and denial of service

## Summary
Severity: High
Advisory: GHSA-vr64-r9qj-h27f
CVE: CVE-2024-22871
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-vr64-r9qj-h27f
Type: github-advisory

## Affected
- Maven: `org.clojure:clojure` — affected >=1.7.0 <1.11.2
- Maven: `org.clojure:clojure` — affected >=1.12.0-alpha1 <1.12.0-alpha9

## Details
Any program on the JVM may read serialized objects via [java.io.ObjectInputStream.readObject()](https://docs.oracle.com/javase/8/docs/api/java/io/ObjectInputStream.html#readObject--). Reading serialized objects from an untrusted source is **inherently unsafe** (this affects any program running on any version of the JVM) and is a prerequisite for this vulnerability.

Clojure classes that represent infinite seqs (Cycle, infinite Repeat, and Iterate) do not define hashCode() and use the parent ASeq.hashCode(), which walks the seq to compute the hash, yielding an infinite loop. Classes like java.util.HashMap call hashCode() on keys during deserialization of a serialized map. 

The exploit requires:

1. Crafting a serialized HashMap object with an infinite seq object as a key.
2. Sending that to a program that reads serialized objects via ObjectInputStream.readObject().

This will cause the program to enter an infinite loop on the reading thread and thus a denial of service (DoS). 

The affected Clojure classes (Cycle, Repeat, Iterate) exist in Clojure 1.7.0-1.11.1, 1.12.0-alpha1-1.12.0-alpha8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22871
- https://clojure.atlassian.net/browse/CLJ-2839
- https://github.com/clojure/clojure
- https://hackmd.io/%40fe1w0/rymmJGida
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/25FKUOYXQZGGJMFUM5HJABWMIX2TILRV
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SWWK2SO2MH4SXPO6L444MM6LHVLVFULV
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YFPGUDXMW6OXKIDGCOZFEAXO74VQIB2T
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/25FKUOYXQZGGJMFUM5HJABWMIX2TILRV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SWWK2SO2MH4SXPO6L444MM6LHVLVFULV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YFPGUDXMW6OXKIDGCOZFEAXO74VQIB2T
