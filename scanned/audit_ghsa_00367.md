# [C] Cryptographically Weak Pseudo-Random Number Generator (PRNG) in akka-actor

## Summary
Severity: Critical
Advisory: GHSA-mr95-9rr4-668f
CVE: CVE-2018-16115
CWE: CWE-338
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-10-22
Source: https://github.com/advisories/GHSA-mr95-9rr4-668f
Type: github-advisory

## Affected
- Maven: `com.typesafe.akka:akka-actor_2.11` — affected >=2.5.0 <2.5.16
- Maven: `com.typesafe.akka:akka-actor_2.12` — affected >=2.5.0 <2.5.16

## Details
Lightbend Akka 2.5.x before 2.5.16 allows message disclosure and modification because of an RNG error. A random number generator is used in Akka Remoting for TLS (both classic and Artery Remoting). Akka allows configuration of custom random number generators. For historical reasons, Akka included the AES128CounterSecureRNG and AES256CounterSecureRNG random number generators. The implementations had a bug that caused the generated numbers to be repeated after only a few bytes. The custom RNG implementations were not configured by default but examples in the documentation showed (and therefore implicitly recommended) using the custom ones. This can be used by an attacker to compromise the communication if these random number generators are enabled in configuration. It would be possible to eavesdrop, replay, or modify the messages sent with Akka Remoting/Cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16115
- https://doc.akka.io/docs/akka/current/security/2018-08-29-aes-rng.html
- https://github.com/advisories/GHSA-mr95-9rr4-668f
