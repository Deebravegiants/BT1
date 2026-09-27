# [H] Traefik docker container using 100% CPU

## Summary
Severity: High
Advisory: GHSA-6fwg-jrfw-ff7p
CVE: CVE-2023-47633
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-6fwg-jrfw-ff7p
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.10.6
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.0.0-beta5

## Details
### Summary

The traefik docker container uses 100% CPU when it serves as its own backend, which is an automatically generated route resulting from the Docker integration in the default configuration.

### Details

While attempting to set up Traefik to handle traffic for Docker containers, I observed in the webUI a rule with the following information:

`Host(traefik-service) | webwebsecure | traefik-service@docker | traefik-service`

I assumed that this is something internal; however, I wondered why it would have a host rule on the web entrypoint configured.

So I have send a request with that hostname with `curl -v --resolve "traefik-service:80:xxx.xxx.xxx.xxx" http://traefik-service`. That made my whole server unresponsive.

I assume the name comes from a docker container with that name, traefik itself:
```
localhost ~ # docker ps
CONTAINER ID   IMAGE                                                   COMMAND                  CREATED             STATUS         PORTS                                                                                                NAMES
d1414e74aec7   traefik:v2.10                                           "/entrypoint.sh trae…"   4 minutes ago       Up 4 minutes   0.0.0.0:80->80/tcp, :::80->80/tcp, 0.0.0.0:443->443/tcp, :::443->443/tcp, 127.0.0.1:8080->8080/tcp   traefik.service
```

### PoC

1. Start traefik with `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -p 80:80 --name foo -p 8080:8080 traefik:v2.10 --api.insecure=true --providers.docker`

2. `curl -v --resolve "foo:80:127.0.0.1" http://foo`

looks like this creates an endless loop of request.

Knowing the name of the docker container seems to be enough to trigger this, if the docker backend is used.

### Impact

Server is unreachable and uses 100% CPU

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-6fwg-jrfw-ff7p
- https://nvd.nist.gov/vuln/detail/CVE-2023-47633
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.10.6
- https://github.com/traefik/traefik/releases/tag/v3.0.0-beta5
