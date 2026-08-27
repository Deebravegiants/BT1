[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** pkg/apis/core/validation/validation.go (L1-1)
```go
/*
```

**File:** pkg/registry/core/resourcequota/strategy.go (L66-71)
```go
// PrepareForUpdate clears fields that are not allowed to be set by end users on update.
func (resourcequotaStrategy) PrepareForUpdate(ctx context.Context, obj, old runtime.Object) {
	newResourcequota := obj.(*api.ResourceQuota)
	oldResourcequota := old.(*api.ResourceQuota)
	newResourcequota.Status = oldResourcequota.Status
}
```

**File:** pkg/registry/core/resourcequota/strategy.go (L120-124)
```go
// ValidateUpdate is the default update validation for an end user.
func (resourcequotaStrategy) ValidateUpdate(ctx context.Context, obj, old runtime.Object) field.ErrorList {
	newObj, oldObj := obj.(*api.ResourceQuota), old.(*api.ResourceQuota)
	return validation.ValidateResourceQuotaUpdate(newObj, oldObj)
}
```
