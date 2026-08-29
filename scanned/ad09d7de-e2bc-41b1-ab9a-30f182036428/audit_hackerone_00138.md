# [M] SSRF for kube-apiserver cloudprovider scene

## Summary
Severity: Medium (CVSS 6.8)
Program: Kubernetes
Weakness: Server-Side Request Forgery (SSRF)
Reporter: lazydog
State: resolved
Disclosed: 2021-10-07T18:03:40.296Z
CVE: CVE-2020-8561
Source: https://hackerone.com/reports/941178

## Details
Report Submission Form

## Summary:
attacker can create admissionwebhook cause ssrf in cloudprovider server.
cloudprovider like GKE AKS EKS.

## Kubernetes Version:
kubernetes v1.18.6

## Component Version:
Docker version 19.03.6, build 369ce74a3c

## Steps To Reproduce:
1. use follwing command create v1.18.6 kubernetes, wait for the download  process done. 

`minikube start --vm-driver=none --kubernetes-version='v1.18.6'`

2.edit `kube-apiserver` options in following path.

```
/etc/kubernetes/manifests/kube-apiserver.yaml

add some options to  spec.containers.command field.  see pic1
--log-dir=/var/log
--logtostderr=false
```

{F920720}

3.save following yaml file to disk as poc1.yaml, and run command` kubectl create poc1.yaml`.

poc1.yaml 
```
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: test.config.xxx.io
webhooks:
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/941178_
