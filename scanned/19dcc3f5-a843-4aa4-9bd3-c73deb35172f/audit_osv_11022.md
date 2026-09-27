# [H] CVE-2017-5652

## Summary
Severity: High
Advisory: CVE-2017-5652
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-5652
Type: osv

## Details
During a routine security analysis, it was found that one of the ports in Apache Impala (incubating) 2.7.0 to 2.8.0 sent data in plaintext even when the cluster was configured to use TLS. The port in question was used by the StatestoreSubscriber class which did not use the appropriate secure Thrift transport when TLS was turned on. It was therefore possible for an adversary, with access to the network, to eavesdrop on the packets going to and coming from that port and view the data in plaintext.

## References
- http://www.securityfocus.com/archive/1/540831/100/0/threaded
- https://lists.apache.org/thread.html/5bab4424f23aebefc8108a0e30273c2a543a289df8113c461f930143%40%3Cdev.impala.apache.org%3E
