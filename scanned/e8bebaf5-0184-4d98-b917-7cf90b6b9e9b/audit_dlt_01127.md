# [M] Ethereum ABI decoder DoS when parsing ZST

## Summary
Severity: Medium
Chain: eth-abi
Component: eth-abi
CWE: Uncontrolled Resource Consumption
Published: 2023-11-24
Source: https://github.com/advisories/GHSA-rqr8-pxh7-cq3g
Type: github-advisory

## Details
With this notification I would like to inform about a DoS vector in the Ethereum ABI decoder. 
We have not yet found a way to exploit this with high impact, still the bug could potentially lead to a DoS in server systems.

Feel free to ask about an extension of the embargo period.

Trail of Bits is informing you and other vendors as a community service, and so we do not seek a bug bounty on these issues.

## BUG DESCRIPTION

Parsers must be written in a robust way, which avoids for example unrecoverable crashes, misinterpretation, hangs, or excessive resource consumption. The recent news about the aCropalypse bug also highlights that more subtle bugs like blind spots in file formats can lead to serious implications. Sometimes the specifications are at fault and sometimes the implementations.

In the case of the Ethereum ABI, I have to blame the specification more than the vulnerable implementations. The specification allows zero-sized-types (ZST), which can cause denial-of-service upon parsing a malicious payload and schema. If a ZST takes zero bytes when stored on disk, but after parsing occupies memory, then there is the possibility for a denial of service.

For instance, what will happen if a parser expects an array of ZST? It will try to parse as many ZST as the byte array claims to contain. The following figure first shows a payload of 20 bytes which will deserialize to an array of the numbers 2, 1, 3. The second payload will deserialize to 232 elements of a ZST like an empty tuple or empty array. 

20 bytes of data:
```
length=0x3u64 2u32 1u32 3u32
```
8 bytes of data
```
length=0xFFFFFFFu64
```

Now, this is not a problem if the individual elements take zero memory after parsing. Though, a common flaw is at least during serialization a large amount of memory will be required. If this case is not handled explicitly in the implementation then we are facing a DoS vector. For example, an implementation could decide to represent an array of ZST differently than a normal array and parse it in constant time, instead of looping and naively adding elements to an in-memory array.

I mentioned that I believe this is a flaw in the specification. The reason for this is that the Ethereum ABI could have decided to disallow ZST completely. Actually, it turned out that in the latest versions of Solidity and Vyper it is not possible to define ZST like empty tuples or empty arrays. Even though the languages do not allow it, it is still allowed in the ABI specification.

## POC

We define the data payload as `0x0000000000000000000000000000000000000000000000000000000000000020 00000000000000000000000000000000000000000000000000000000FFFFFFFF`. It consists of two 32-byte blocks, which describe a serialized array of ZST. The first block defines an offset to the array’s elements. The second block defines the length of the array. Independent of the programming language we will reference it always as payload.

We will try to decode this payload using the ABI schemata ()[] and uint32[0][]. The former represents a dynamic array of empty tuples and the latter a dynamic array of empty static arrays. The distinction between dynamic and static is important here, because an empty static array takes zero bytes, whereas a dynamic one takes a few bytes because it serializes the length of the array.

The following Python program uses the official eth_abi library and will hang and eventually cause an out-of-memory error.

    from eth_abi import decode
    data = bytearray.fromhex(payload)

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-rqr8-pxh7-cq3g_
