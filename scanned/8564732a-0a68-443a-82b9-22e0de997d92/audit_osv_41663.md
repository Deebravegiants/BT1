# [M] CMP Indefinite Cache Growth of ExtraCerts

## Summary
Severity: Medium
Advisory: CVE-2026-63074
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-63074
Type: osv

## Details
Issue summary: The OpenSSL Certificate Management Protocol (CMP) caches
additional certificates (extraCerts) sent in a CMP message, but never expunges
them (for instance if they are invalid).  If a server reuses an OSSL_CMP_CTX
frequently, this cache of extraCerts may grow unboundedly, and a malicious
client may flood a CMP server with requests driving this growth.

Impact summary: Users utilizing a CMP server that reuses a single OSSL_CMP_CTX
for the lifetime of a server process may observe unbounded memory growth in the
event a malicious client repeatedly sends requests containing unique extra
certificates, which may lead to OOM conditions.

CWE: CWE-770: Allocation of Resources Without Limits or Throttling

Description: If a remote user sends CMP messages to a server with a list of
extraCerts and the message is rejected, the extraCerts from the message remains
in the server contexts untrusted certificate stack.  This exposes servers with
long lived ctx objects to Denial of Service attacks in which an attacker sends
messages intending to be rejected with a large list of additional certificates
repeatedly, forcing the server to store them indefinitely.
   
The issue was fixed by removing the added extra certs if the message is
rejected, using the same method as when the context is configured to not do
caching at all.

FIPS impact: no
As the CMP code lives outside the FIPS module boundary, no FIPS
modules are affected by this CVE.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63074.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63074
- https://openssl-library.org/news/secadv/20260825.txt
- https://github.com/openssl/openssl/commit/01e567978a55fba18142a230380c31296049fae7
- https://github.com/openssl/openssl/commit/21a5d9658b0c66daace60e10ea18ff32a448de9f
- https://github.com/openssl/openssl/commit/74ae7f6df47a5767c1010b88c47507dfc5b32c46
- https://github.com/openssl/openssl/commit/75360af9650d4e0c82ba0050c5c9912cd79e54af
- https://github.com/openssl/openssl/commit/f636f9ca0fa1bae5b42f9e787f025c96fb09c43a
