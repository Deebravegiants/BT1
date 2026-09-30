# [?] op-deployer: fix nil dereference of SuperchainRoles (#13178)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-12-03
Source: https://github.com/bobanetwork/boba/commit/a46cc6163b0eacb1e86097259bb6b50419975e4d
Type: security-commit

## Details
op-deployer: fix nil dereference of SuperchainRoles (#13178)

## Patch
### op-deployer/pkg/deployer/state/intent.go
```diff
@@ -98,6 +98,9 @@ func (c *Intent) validateCustomConfig() error {
 		return ErrL2ContractsLocatorUndefined
 	}
 
+	if c.SuperchainRoles == nil {
+		return errors.New("SuperchainRoles is set to nil")
+	}
 	if err := c.SuperchainRoles.CheckNoZeroAddresses(); err != nil {
 		return err
 	}
@@ -149,7 +152,7 @@ func (c *Intent) validateStandardValues() error {
 	if err != nil {
 		return fmt.Errorf("error getting standard superchain roles: %w", err)
 	}
-	if *c.SuperchainRoles != *standardSuperchainRoles {
+	if c.SuperchainRoles == nil || *c.SuperchainRoles != *standardSuperchainRoles {
 		return fmt.Errorf("SuperchainRoles does not match standard value")
 	}
 
```
