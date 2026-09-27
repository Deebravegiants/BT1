# [M] Observable Differences in Behavior to Error Inputs in Bouncy Castle

## Summary
Severity: Medium
Advisory: GHSA-72m5-fvvv-55m6
CVE: CVE-2020-26939
CWE: CWE-203
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-72m5-fvvv-55m6
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.61
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=0 <1.61
- Maven: `org.bouncycastle:bcprov-jdk16` — affected >=0 <1.61
- Maven: `org.bouncycastle:bc-fips` — affected >=0 <1.0.2
- Maven: `org.bouncycastle:bcprov-ext-jdk15on` — affected >=0 <1.61
- Maven: `org.bouncycastle:bcprov-ext-jdk16` — affected >=0 <1.61
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.61
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=0 <1.61

## Details
In Legion of the Bouncy Castle BC before 1.55 and BC-FJA before 1.0.2, attackers can obtain sensitive information about a private exponent because of Observable Differences in Behavior to Error Inputs. This occurs in org.bouncycastle.crypto.encodings.OAEPEncoding. Sending invalid ciphertext that decrypts to a short payload in the OAEP Decoder could result in the throwing of an early exception, potentially leaking some information about the private exponent of the RSA private key performing the encryption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26939
- https://github.com/bcgit/bc-java/commit/930f8b274c4f1f3a46e68b5441f1e7fadb57e8c1
- https://github.com/bcgit/bc-java/wiki/CVE-2020-26939
- https://lists.apache.org/thread.html/r8c36ba34e80e05eecb1f80071cc834d705616f315b634ec0c7d8f42e%40%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/r8c36ba34e80e05eecb1f80071cc834d705616f315b634ec0c7d8f42e@%3Cissues.solr.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/11/msg00007.html
- https://security.netapp.com/advisory/ntap-20201202-0005
