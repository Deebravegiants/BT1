# [C] ObjectInputStream.readObject() without ObjectInputFilter in fabric-sdk-java allows Java deserialization RCE

## Summary
Severity: Critical
Chain: Hyperledger Fabric
Component: hyperledger/fabric
CVE: CVE-2026-41586
CWE: Deserialization of Untrusted Data
Published: 2026-04-22
Source: https://github.com/hyperledger/fabric/security/advisories/GHSA-prf8-cf2x-rhx7
Type: github-advisory

## Details
## Summary

This advisory covers the deprecated `fabric-sdk-java` client SDK. `Channel.java` implements `readObject()` and exposes `deSerializeChannel()` which call `ObjectInputStream.readObject()` on untrusted byte arrays without configuring an `ObjectInputFilter`. This is the classic Java deserialization RCE pattern.

**Note:** `fabric-sdk-java` is deprecated and maintained in https://github.com/hyperledger/fabric-sdk-java. Filing here as that repo does not have private vulnerability reporting enabled.

## Affected Code

```java
// src/main/java/org/hyperledger/fabric/sdk/Channel.java
private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
    in.defaultReadObject();  // No ObjectInputFilter configured
}

public Channel deSerializeChannel(byte[] channelBytes)
        throws IOException, ClassNotFoundException, InvalidArgumentException {
    ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(channelBytes));
    Channel channel = (Channel) ois.readObject();  // Untrusted bytes deserialized
    return channel;
}
```

## Attack Vector

An attacker who can supply crafted serialized Channel bytes to the client application — for example, by compromising a local channel file, injecting data through an application that accepts Channel bytes from external sources, or exploiting a separate write primitive — can achieve RCE via gadget chain exploitation when deSerializeChannel() processes those bytes. The risk is highest in deployments that accept Channel data from sources outside the client's direct control. Note: channel data is not transmitted from Fabric peers; this is a client-side deserialization surface.

## Proof of Concept

```java
// Generate malicious payload with ysoserial:
// java -jar ysoserial.jar CommonsCollections6 "touch /tmp/pwned" > malicious_channel.ser

// Victim code:
byte[] maliciousBytes = Files.readAllBytes(Paths.get("malicious_channel.ser"));
Channel channel = client.deSerializeChannel(maliciousBytes);  // RCE fires here
```

## Notes on Deprecation

fabric-sdk-java is deprecated as of Hyperledger Fabric v2.5 (replaced by `org.hyperledger.fabric:fabric-gateway`). However, organizations that have not yet migrated remain fully exposed. Automated dependency scanners (Snyk, Dependabot) cannot alert users without a published GHSA. This advisory is filed to ensure those users are notified and directed to migrate.

## Fix

For the deprecated SDK: add `ObjectInputFilter` to whitelist only expected classes:

```java
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
    "org.hyperledger.fabric.sdk.*;java.util.*;java.lang.*;!*"
);
ois.setObjectInputFilter(filter);
```

**The recommended remediation is migration to `org.hyperledger.fabric:fabric-gateway`**, which does not use Java serialization.

## References

- CWE-502: Deserialization of Untrusted Data
- Migration guide: https://hyperledger.github.io/fabric-gateway/

## Credits

Found via independent security research.
