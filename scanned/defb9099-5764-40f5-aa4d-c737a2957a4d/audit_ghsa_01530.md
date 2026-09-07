# [H] Denial of service due to reference expansion in versions earlier than 4.0

## Summary
Severity: High
Advisory: GHSA-mm44-wc5p-wqhq
Ecosystem: Maven
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-mm44-wc5p-wqhq
Type: github-advisory

## Affected
- Maven: `com.upokecenter:cbor` — affected >=0 <4.0.0

## Details
### Impact

The CBOR library supports optional tags that enable CBOR objects to contain references to objects within them. Versions earlier than 4.0 resolved those references automatically. While this by itself doesn't cause much of a security problem, a denial of service can happen if those references are deeply nested and used multiple times (so that the same reference to the same object occurs multiple times), and if the decoded CBOR object is sent to a serialization method such as EncodeToBytes, ToString, or ToJSONString, since the objects referred to are expanded in the process and take up orders of magnitude more memory than if the references weren't resolved.

The impact of this problem on any particular system varies. In general, the risk is higher if the system allows users to send arbitrary CBOR objects without authentication, or exposes a remote endpoint in which arbitrary CBOR objects can be sent without authentication.

### Patches

This problem is addressed in version 4.0 by disabling reference resolution by default. Users should use the latest version of this library.

### Workarounds

Since version 3.6, an encoding option (`resolvereferences=true` or `resolvereferences=false`) in CBOREncodeOptions sets whether the CBOR processor will resolve these kinds of references when decoding a CBOR object. Set `resolvereferences=false` to disable reference resolution.

In version 3.6, if the method used CBORObject.Read() or CBORObject.DecodeFromBytes() to decode a serialized CBOR object, call the overload that takes CBOREncodeOptions as follows:

    CBORObject.DecodeFromBytes(bytes, new CBOREncodeOptions("resolvereferences=false"));

In versions 3.5 and earlier, this issue is present only if the CBOR object is an array or a map. If the application does not expect a decoded CBOR object to be an array or a map, it should check the CBOR object's type before encoding that object, as follows:

    if (cbor.Type != CBORType.Array && cbor.Type != CBORType.Map) {
       cbor.EncodeToBytes();
    }

Alternatively, for such versions, the application can use WriteTo to decode the CBOR object to a so-called "limited memory stream", that is, a Stream that throws an exception if too many bytes would be written. How to write such a limited-memory stream is nontrivial and beyond the scope of this advisory.

    LimitedMemoryStream stream = new LimitedMemoryStream(100000); // Limit to 100000 bytes
    cbor.WriteTo(stream);
    return stream.ToBytes();

To check whether a byte array representing a CBOR object might exhibit this problem, check whether the array contains the byte 0xd8 followed immediately by either 0x19 or 0x1d. This check catches all affected CBOR objects but may catch some non-affected CBOR objects (notably integers and byte strings).

### References

See the Wikipedia article [Billion laughs attack](https://en.wikipedia.org/wiki/Billion_laughs_attack) and the related issue in [Kubernetes](https://github.com/kubernetes/kubernetes/issues/83253).

### For more information

If you have any questions or comments about this advisory, open an issue in [the CBOR repository](https://github.com/peteroupc/cbor-java).

## References
- https://github.com/peteroupc/CBOR-Java/security/advisories/GHSA-mm44-wc5p-wqhq
- https://github.com/peteroupc/CBOR-Java
