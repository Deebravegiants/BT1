# [H] Code inject via nginx.ingress.kubernetes.io/permanent-redirect annotation

## Summary
Severity: High (CVSS 7.6)
Program: Kubernetes
Weakness: Code Injection
Reporter: jkroepke
State: resolved
Disclosed: 2023-10-25T22:46:43.792Z
CVE: CVE-2023-5044
Source: https://hackerone.com/reports/2039464

## Details
Report Submission Form

## Summary:
The value of the `nginx.ingress.kubernetes.io/permanent-redirect` annotation will be not sanitized and passed into the nginx configuration. This leads into a code inject from any user that is allowed to create ingress objects.

## Kubernetes Version:
v1.26.3 (minikube)

## Component Version:
```
-------------------------------------------------------------------------------
NGINX Ingress controller
  Release:       v1.8.0
  Build:         35f5082ee7f211555aaff431d7c4423c17f8ce9e
  Repository:    https://github.com/kubernetes/ingress-nginx
  nginx version: nginx/1.21.6

-------------------------------------------------------------------------------
```

## Steps To Reproduce:

  1. Install ingress-nginx, using latest version and default values. For demo purpose, I set `allow-snippet-annotations=false`
        ```bash
        helm upgrade -i ingress-nginx ingress-nginx/ingress-nginx -f values.yaml # values.yaml is attached
        ```
  1. apply service and ingress object from attachments
        ```bash
        k apply -f ingress.yaml #ingress.yaml is attached
        ```
  1. Optional: If ingress-nginx is not exposed, run `kubectl port-forward deploy/ingress-nginx-controller 8080:80` and continue step 4 in a separate shell.
  1. Validate, if the code is injected. This demo uses the hostname `kubernetes.api`, use the `--resolve` parameter of curl to do an request for the hidden server instance. The code below expect that ingress-nginx is accessible trough 127.0.0.1:8080

        ```bash
        curl -v --resolve "kubernetes.api:8080:127.0.0.1" http://kubernetes.api:8080/api/v1/namespaces/kube-system/secrets/
        ```

## Supporting Material/References:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2039464_
