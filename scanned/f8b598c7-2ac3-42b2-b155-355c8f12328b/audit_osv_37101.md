# [H] Docker Model Runner Unauthenticated Runtime Flag Injection via _configure Endpoint

## Summary
Severity: High
Advisory: CVE-2026-28400
Aliases: GHSA-m456-c56c-hh5c
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28400
Type: osv

## Details
Docker Model Runner (DMR) is software used to manage, run, and deploy AI models using Docker. Versions prior to 1.0.16 expose a  POST `/engines/_configure`  endpoint that accepts arbitrary runtime flags without authentication. These flags are passed directly to the underlying inference server (llama.cpp). By injecting the  --log-file  flag, an attacker with network access to the Model Runner API can write or overwrite arbitrary files accessible to the Model Runner process. When bundled with Docker Desktop (where Model Runner is enabled by default since version 4.46.0), it is reachable from any default container at  model-runner.docker.internal  without authentication. In this context, the file overwrite can target the Docker Desktop VM disk (`Docker.raw` ), resulting in the destruction of all containers, images, volumes, and build history. However, in specific configurations and with user interaction, it is possible to convert this vulnerability in a container escape. The issue is fixed in Docker Model Runner 1.0.16. Docker Desktop users should update to 4.61.0 or later, which includes the fixed Model Runner. A workaround is available. For Docker Desktop users, enabling Enhanced Container Isolation (ECI) blocks container access to Model Runner, preventing exploitation. However, if the Docker Model Runner is exposed to localhost over TCP in specific configurations, the vulnerability is still exploitable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28400.json
- https://github.com/docker/model-runner/security/advisories/GHSA-m456-c56c-hh5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-28400
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-28379
