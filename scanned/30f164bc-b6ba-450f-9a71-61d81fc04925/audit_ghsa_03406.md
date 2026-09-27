# [H] Jetty vulnerable to incorrect handling of invalid large TLS frame, exhausting CPU resources

## Summary
Severity: High
Advisory: GHSA-26vr-8j45-3r4w
CVE: CVE-2021-28165
CWE: CWE-400, CWE-551, CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-26vr-8j45-3r4w
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=7.2.2 <9.4.39
- Maven: `org.eclipse.jetty:jetty-server` — affected >=10.0.0 <10.0.2
- Maven: `org.eclipse.jetty:jetty-server` — affected >=11.0.0 <11.0.2

## Details
### Impact
When using SSL/TLS with Jetty, either with HTTP/1.1, HTTP/2, or WebSocket, the server may receive an invalid large (greater than 17408) TLS frame that is incorrectly handled, causing CPU resources to eventually reach 100% usage.

### Workarounds

The problem can be worked around by compiling the following class:
```java
package org.eclipse.jetty.server.ssl.fix6072;

import java.nio.ByteBuffer;
import javax.net.ssl.SSLEngine;
import javax.net.ssl.SSLEngineResult;
import javax.net.ssl.SSLException;
import javax.net.ssl.SSLHandshakeException;

import org.eclipse.jetty.io.EndPoint;
import org.eclipse.jetty.io.ssl.SslConnection;
import org.eclipse.jetty.server.Connector;
import org.eclipse.jetty.server.SslConnectionFactory;
import org.eclipse.jetty.util.BufferUtil;
import org.eclipse.jetty.util.annotation.Name;
import org.eclipse.jetty.util.ssl.SslContextFactory;

public class SpaceCheckingSslConnectionFactory extends SslConnectionFactory
{
    public SpaceCheckingSslConnectionFactory(@Name("sslContextFactory") SslContextFactory factory, @Name("next") String nextProtocol)
    {
        super(factory, nextProtocol);
    }

    @Override
    protected SslConnection newSslConnection(Connector connector, EndPoint endPoint, SSLEngine engine)
    {
        return new SslConnection(connector.getByteBufferPool(), connector.getExecutor(), endPoint, engine, isDirectBuffersForEncryption(), isDirectBuffersForDecryption())
        {
            @Override
            protected SSLEngineResult unwrap(SSLEngine sslEngine, ByteBuffer input, ByteBuffer output) throws SSLException
            {
                SSLEngineResult results = super.unwrap(sslEngine, input, output);

                if ((results.getStatus() == SSLEngineResult.Status.BUFFER_UNDERFLOW ||
                    results.getStatus() == SSLEngineResult.Status.OK && results.bytesConsumed() == 0 && results.bytesProduced() == 0) &&
                    BufferUtil.space(input) == 0)
                {
                    BufferUtil.clear(input);
                    throw new SSLHandshakeException("Encrypted buffer max length exceeded");
                }
                return results;
            }
        };
    }
}
```
This class can be deployed by:
 + The resulting class file should be put into a jar file (eg sslfix6072.jar)
 + The jar file should be made available to the server. For a normal distribution this can be done by putting the file into ${jetty.base}/lib
 + Copy the file `${jetty.home}/modules/ssl.mod` to `${jetty.base}/modules`
 + Edit the `${jetty.base}/modules/ssl.mod` file to have the following section:

```
[lib]
lib/sslfix6072.jar
```

+ Copy the file `${jetty.home}/etc/jetty-https.xml` and`${jetty.home}/etc/jetty-http2.xml` to `${jetty.base}/etc`
+ Edit files `${jetty.base}/etc/jetty-https.xml` and `${jetty.base}/etc/jetty-http2.xml`, changing any reference of `org.eclipse.jetty.server.SslConnectionFactory` to `org.eclipse.jetty.server.ssl.fix6072.SpaceCheckingSslConnectionFactory`. For example:
```xml
  <Call name="addIfAbsentConnectionFactory">
    <Arg>
      <New class="org.eclipse.jetty.server.ssl.fix6072.SpaceCheckingSslConnectionFactory">
        <Arg name="next">http/1.1</Arg>
        <Arg name="sslContextFactory"><Ref refid="sslContextFactory"/></Arg>
      </New>
    </Arg>
  </Call>
```
+ Restart Jetty

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-26vr-8j45-3r4w
- https://nvd.nist.gov/vuln/detail/CVE-2021-28165
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://lists.apache.org/thread.html/rc907ed7b089828364437de5ed57fa062330970dc1bc5cd214b711f77@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rc6c43c3180c0efe00497c73dd374cd34b62036cb67987ad42c1f2dce@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rc4dbc9907b0bdd634200ac90a15283d9c143c11af66e7ec72128d020@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rc4779abc1cface47e956cf9f8910f15d79c24477e7b1ac9be076a825@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbd9a837a18ca57ac0d9b4165a6eec95ee132f55d025666fe41099f33@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rbcd7b477df55857bb6cae21fcc4404683ac98aac1a47551f0dc55486@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbc075a4ac85e7a8e47420b7383f16ffa0af3b792b8423584735f369f@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/rbba0b02a3287e34af328070dd58f7828612f96e2e64992137f4dc63d@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbab9e67ec97591d063905bc7d4743e6a673f1bc457975fc0445ac97f@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/rb8f5a6ded384eb00608e6137e87110e7dd7d5054cc34561cb89b81af@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rb66ed0b4bb74836add60dd5ddf9172016380b2aeefb7f96fe348537b@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rb2d34abb67cdf525945fe4b821c5cdbca29a78d586ae1f9f505a311c@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rb1624b9777a3070135e94331a428c6653a6a1edccd56fa9fb7a547f2@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rb11a13e623218c70b9f2a2d0d122fdaaf905e04a2edcd23761894464@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rb00345f6b1620b553d2cc1acaf3017aa75cea3776b911e024fa3b187@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/raea6e820644e8c5a577f77d4e2044f8ab52183c2536b00c56738beef@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rae8bbc5a516f3e21b8a55e61ff6ad0ced03bdbd116d2170a3eed9f5c@%3Creviews.spark.apache.org%3E
