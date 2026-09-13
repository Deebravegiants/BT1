# [H] http4s has HTTP/2 Denial of Service with Ember Backend

## Summary
Severity: High
Advisory: GHSA-vmm3-xgcx-67hm
CVE: CVE-2026-54556
CWE: CWE-409
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-vmm3-xgcx-67hm
Type: github-advisory

## Affected
- Maven: `org.http4s:http4s-ember-core_2.12` — affected >=0 <0.23.35
- Maven: `org.http4s:http4s-ember-core_2.13` — affected >=1.0.0-M1 <1.0.0-M47
- Maven: `org.http4s:http4s-ember-core_3` — affected >=0 <0.23.35
- Maven: `org.http4s:http4s-ember-core_3` — affected >=1.0.0-M1 <1.0.0-M47
- Maven: `org.http4s:http4s-ember-core_2.13` — affected >=0 <0.23.35

## Details
### Summary

http4s 0.23.x and 1.0 servers running ember with http2 enabled are vulnerable to a denial of service attack using a HPACK bomb vulnerability recently disclosed as affecting other http2 servers.

### Impact

Denial of Service:
- Affects any http4s server running the ember backend with HTTP/2 enabled that is exposed to untrusted traffic.
- Affects any http4s client running the ember backend with HTTP/2 enabled that can be directed to an untrusted server.

### Details

The issue occurs in the [Hpack wrapper](https://github.com/http4s/http4s/blob/c63fbff43dfe7e3bec25b789fd0a0027ec40ed62/ember-core/shared/src/main/scala/org/http4s/ember/core/h2/Hpack.scala#L54). Ember concatenates the header and continuation frames before decoding all headers at once. When the code decodes the attack payload, the relatively small packets decode to a significantly larger amount of data which is returned as a single List which is then held in memory for further processing. With enough concurrent connections (~5 with a 2GB heap in testing) this leads to an OOM, eg:

```
java.lang.OutOfMemoryError: Java heap space
        at scala.collection.mutable.ListBuffer.scala$collection$mutable$ListBuffer$$freshFrom(ListBuffer.scala:129)
        at scala.collection.mutable.ListBuffer.addAll(ListBuffer.scala:147)
        at scala.collection.mutable.ListBuffer.addAll(ListBuffer.scala:40)
        at scala.collection.mutable.Growable.$plus$plus$eq(Growable.scala:69)
        at scala.collection.mutable.Growable.$plus$plus$eq$(Growable.scala:69)
        at scala.collection.mutable.AbstractBuffer.$plus$plus$eq(Buffer.scala:314)
        at org.http4s.Header$.org$http4s$Header$ToRaw$$anon$10$$_$$lessinit$greater$$anonfun$2(Header.scala:192)
        at org.http4s.Header$ToRaw$$anon$10$$Lambda/0x00001fe001239c50.apply(Unknown Source)
        at scala.collection.immutable.List.foreach(List.scala:334)
        at org.http4s.Header$ToRaw$$anon$10.<init>(Header.scala:192)
        at org.http4s.Header$ToRaw$.scalaCollectionSeqToRaw(Header.scala:195)
        at org.http4s.Headers$.apply(Headers.scala:220)
        at org.http4s.ember.core.h2.PseudoHeaders$.headersToRequestNoBody(PseudoHeaders.scala:95)
        at org.http4s.ember.core.h2.H2Stream.receiveHeaders$$anonfun$1$$anonfun$2$$anonfun$3$$anonfun$2(H2Stream.scala:248)
        at org.http4s.ember.core.h2.H2Stream$$Lambda/0x00001fe001511fd8.apply(Unknown Source)
        at cats.effect.IOFiber.runLoop(IOFiber.scala:429)
        at cats.effect.IOFiber.autoCedeR(IOFiber.scala:1460)
        at cats.effect.IOFiber.run(IOFiber.scala:129)
        at cats.effect.unsafe.WorkerThread.run(WorkerThread.scala:935)
```

### Fix
  
The Hpack handling code has a configurable max header size parameter, but it does not include indexed headers in that accounting, allowing the attack to bypass the limit. There is not any configuration available in current http4s versions that can be enabled to prevent this attack short of disabling http2.

A fix has been tested locally that threads the maxHeaderSize setting from the server builder into the Hpack code. Using this, connections can be prematurely terminated once the decoded data size exceeds the maxHeaderSize that users can already configure.

### Workarounds

If you can't upgrade immediately:
- Disable HTTP/2 in Ember backends

## References
- https://github.com/http4s/http4s/security/advisories/GHSA-vmm3-xgcx-67hm
- https://github.com/http4s/http4s/commit/6e8eccd64a6a74ab4811897881e95e0e1b3a818e
- https://github.com/http4s/http4s
- https://github.com/http4s/http4s/releases/tag/v0.23.35
- https://github.com/http4s/http4s/releases/tag/v1.0.0-M47
