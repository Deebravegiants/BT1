# [H] CVE-2021-40829

## Summary
Severity: High
Advisory: CVE-2021-40829
Aliases: GHSA-743r-5g92-5vgf, PYSEC-2021-862
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-23
Source: https://osv.dev/vulnerability/CVE-2021-40829
Type: osv

## Details
Connections initialized by the AWS IoT Device SDK v2 for Java (versions prior to 1.4.2), Python (versions prior to 1.6.1), C++ (versions prior to 1.12.7) and Node.js (versions prior to 1.5.3) did not verify server certificate hostname during TLS handshake when overriding Certificate Authorities (CA) in their trust stores on MacOS. This issue has been addressed in aws-c-io submodule versions 0.10.5 onward. This issue affects: Amazon Web Services AWS IoT Device SDK v2 for Java versions prior to 1.4.2 on macOS. Amazon Web Services AWS IoT Device SDK v2 for Python versions prior to 1.6.1 on macOS. Amazon Web Services AWS IoT Device SDK v2 for C++ versions prior to 1.12.7 on macOS. Amazon Web Services AWS IoT Device SDK v2 for Node.js versions prior to 1.5.3 on macOS. Amazon Web Services AWS-C-IO 0.10.4 on macOS.

## References
- https://github.com/awslabs/aws-c-io/
- https://github.com/aws/aws-iot-device-sdk-cpp-v2
- https://github.com/aws/aws-iot-device-sdk-java-v2
- https://github.com/aws/aws-iot-device-sdk-js-v2
- https://github.com/aws/aws-iot-device-sdk-python-v2
