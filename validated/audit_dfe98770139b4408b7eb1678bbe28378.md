[1](#0-0) [2](#0-1)

### Citations

**File:** pkg/registry/core/serviceaccount/storage/token.go (L180-187)
```go
			podObj, err := r.pods.Get(newCtx, ref.Name, &metav1.GetOptions{})
			if err != nil {
				return nil, err
			}
			pod = podObj.(*api.Pod)
			if name != pod.Spec.ServiceAccountName {
				return nil, errors.NewBadRequest(fmt.Sprintf("cannot bind token for serviceaccount %q to pod running with different serviceaccount name.", name))
			}
```

**File:** pkg/registry/core/serviceaccount/storage/token.go (L291-291)
```go
	sc, pc, err := token.Claims(*svcacct, pod, secret, node, validating, mutating, exp, warnAfter, req.Spec.Audiences, attestations)
```
