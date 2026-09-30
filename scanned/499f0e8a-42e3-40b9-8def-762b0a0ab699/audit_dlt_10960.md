# [?] fix: remove panic when iterating constraints

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2023-08-18
Source: https://github.com/Consensys-Incorporated/gnark/commit/4abbceadf2c099369ef5477a61acb91b82d0af65
Type: security-commit

## Details
fix: remove panic when iterating constraints

## Patch
### constraint/bls12-377/system.go
```diff
@@ -123,8 +123,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -205,8 +203,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, sparseR1C)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```

### constraint/bls12-381/system.go
```diff
@@ -123,8 +123,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -205,8 +203,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, sparseR1C)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```

### constraint/bls24-315/system.go
```diff
@@ -123,8 +123,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -205,8 +203,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, sparseR1C)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```

### constraint/bls24-317/system.go
```diff
@@ -123,8 +123,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -205,8 +203,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, sparseR1C)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```

### constraint/bn254/system.go
```diff
@@ -123,8 +123,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -205,8 +203,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, sparseR1C)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```

### constraint/bw6-633/system.go
```diff
@@ -123,8 +123,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -205,8 +203,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, sparseR1C)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```

### constraint/bw6-761/system.go
```diff
@@ -123,8 +123,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -205,8 +203,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, sparseR1C)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```

### constraint/tinyfield/system.go
```diff
@@ -123,8 +123,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -205,8 +203,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))
 			toReturn = append(toReturn, sparseR1C)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```

### internal/generator/backend/template/representations/system.go.tmpl
```diff
@@ -109,8 +109,6 @@ func (cs *system) GetR1Cs() []constraint.R1C {
 			var r1c constraint.R1C
 			bc.DecompressR1C(&r1c, inst.Unpack(&cs.System))	
 			toReturn = append(toReturn, r1c)
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
@@ -193,8 +191,6 @@ func (cs *system) GetSparseR1Cs() []constraint.SparseR1C {
 			var sparseR1C constraint.SparseR1C
 			bc.DecompressSparseR1C(&sparseR1C, inst.Unpack(&cs.System))	
 			toReturn = append(toReturn, sparseR1C)	 
-		} else {
-			panic("not implemented")
 		}
 	}
 	return toReturn
```
