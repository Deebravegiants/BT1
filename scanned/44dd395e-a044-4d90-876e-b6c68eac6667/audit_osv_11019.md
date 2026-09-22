# [C] CVE-2017-5645

## Summary
Severity: Critical
Advisory: CVE-2017-5645
Aliases: GHSA-fxph-q3j8-mv87
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-17
Source: https://osv.dev/vulnerability/CVE-2017-5645
Type: osv

## Details
In Apache Log4j 2.x before 2.8.2, when using the TCP socket server or UDP socket server to receive serialized log events from another application, a specially crafted binary payload can be sent that, when deserialized, can execute arbitrary code.

## References
- https://lists.apache.org/thread.html/0dcca05274d20ef2d72584edcf8c917bbb13dbbd7eb35cae909d02e9%40%3Cdev.logging.apache.org%3E
- https://lists.apache.org/thread.html/277b4b5c2b0e06a825ccec565fa65bd671f35a4d58e3e2ec5d0618e1%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/44491fb9cc19acc901f7cff34acb7376619f15638439416e3e14761c%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/479471e6debd608c837b9815b76eab24676657d4444fcfd5ef96d6e6%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/6114ce566200d76e3cc45c521a62c2c5a4eac15738248f58a99f622c%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/84cc4266238e057b95eb95dfd8b29d46a2592e7672c12c92f68b2917%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/8ab32b4c9f1826f20add7c40be08909de9f58a89dc1de9c09953f5ac%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/e8fb7d76a244ee997ba4b217d6171227f7c2521af8c7c5b16cba27bc%40%3Cdev.logging.apache.org%3E
- https://lists.apache.org/thread.html/eea03d504b36e8f870e8321d908e1def1addda16adda04327fe7c125%40%3Cdev.logging.apache.org%3E
- https://lists.apache.org/thread.html/r0831e2e52a390758ce39a6193f82c11c295175adce6e6307de28c287%40%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/r18f1c010b554a3a2d761e8ffffd8674fd4747bcbcf16c643d708318c%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/r23369fd603eb6d62d3b883a0a28d12052dcbd1d6d531137124cd7f83%40%3Cgithub.beam.apache.org%3E
- https://lists.apache.org/thread.html/r2ce8d26154bea939536e6cf27ed02d3192bf5c5d04df885a80fe89b3%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r2ff63f210842a3c5e42f03a35d8f3a345134d073c80a04077341c211%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r3784834e80df2f284577a5596340fb84346c91a2dea6a073e65e3397%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r3a85514a518f3080ab1fc2652cfe122c2ccf67cfb32356acb1b08fe8%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/r3d666e4e8905157f3c046d31398b04f2bfd4519e31f266de108c6919%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r4b25538be50126194cc646836c718b1a4d8f71bd9c912af5b59134ad%40%3Cdev.tika.apache.org%3E
