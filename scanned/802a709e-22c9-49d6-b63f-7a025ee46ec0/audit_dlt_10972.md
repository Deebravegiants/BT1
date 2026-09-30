# [?] fix: cs.Println doesn't trigger panic anymore

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2021-03-15
Source: https://github.com/Consensys-Incorporated/gnark/commit/509c697ae64c0519c606574bc7dfd21b6bf700be
Type: security-commit

## Details
fix: cs.Println doesn't trigger panic anymore

## Patch
### frontend/cs.go
```diff
@@ -349,9 +349,11 @@ func parseLogValue(input interface{}, name string, handler logValueHandler) {
 			return
 		default:
 			for i := 0; i < tValue.NumField(); i++ {
-				value := tValue.Field(i).Interface()
-				_name := appendName(name, tValue.Type().Field(i).Name)
-				parseLogValue(value, _name, handler)
+				if tValue.Field(i).CanInterface() {
+					value := tValue.Field(i).Interface()
+					_name := appendName(name, tValue.Type().Field(i).Name)
+					parseLogValue(value, _name, handler)
+				}
 			}
 		}
 	case reflect.Slice, reflect.Array:
```

### internal/backend/bls377/cs/r1cs.go
```diff
@@ -168,9 +168,10 @@ func (r1cs *R1CS) logValue(entry compiled.LogEntry, wireValues []fr.Element, wir
 	for j := 0; j < len(entry.ToResolve); j++ {
 		wireID := entry.ToResolve[j]
 		if !wireInstantiated[wireID] {
-			panic("wire values was not instantiated")
+			toResolve = append(toResolve, "???")
+		} else {
+			toResolve = append(toResolve, wireValues[wireID].String())
 		}
-		toResolve = append(toResolve, wireValues[wireID].String())
 	}
 	return fmt.Sprintf(entry.Format, toResolve...)
 }
```

### internal/backend/bls381/cs/r1cs.go
```diff
@@ -168,9 +168,10 @@ func (r1cs *R1CS) logValue(entry compiled.LogEntry, wireValues []fr.Element, wir
 	for j := 0; j < len(entry.ToResolve); j++ {
 		wireID := entry.ToResolve[j]
 		if !wireInstantiated[wireID] {
-			panic("wire values was not instantiated")
+			toResolve = append(toResolve, "???")
+		} else {
+			toResolve = append(toResolve, wireValues[wireID].String())
 		}
-		toResolve = append(toResolve, wireValues[wireID].String())
 	}
 	return fmt.Sprintf(entry.Format, toResolve...)
 }
```

### internal/backend/bn256/cs/r1cs.go
```diff
@@ -168,9 +168,10 @@ func (r1cs *R1CS) logValue(entry compiled.LogEntry, wireValues []fr.Element, wir
 	for j := 0; j < len(entry.ToResolve); j++ {
 		wireID := entry.ToResolve[j]
 		if !wireInstantiated[wireID] {
-			panic("wire values was not instantiated")
+			toResolve = append(toResolve, "???")
+		} else {
+			toResolve = append(toResolve, wireValues[wireID].String())
 		}
-		toResolve = append(toResolve, wireValues[wireID].String())
 	}
 	return fmt.Sprintf(entry.Format, toResolve...)
 }
```

### internal/backend/bw761/cs/r1cs.go
```diff
@@ -168,9 +168,10 @@ func (r1cs *R1CS) logValue(entry compiled.LogEntry, wireValues []fr.Element, wir
 	for j := 0; j < len(entry.ToResolve); j++ {
 		wireID := entry.ToResolve[j]
 		if !wireInstantiated[wireID] {
-			panic("wire values was not instantiated")
+			toResolve = append(toResolve, "???")
+		} else {
+			toResolve = append(toResolve, wireValues[wireID].String())
 		}
-		toResolve = append(toResolve, wireValues[wireID].String())
 	}
 	return fmt.Sprintf(entry.Format, toResolve...)
 }
```

### internal/generators/backend/template/representations/r1cs.go.tmpl
```diff
@@ -153,9 +153,10 @@ func (r1cs *R1CS) logValue(entry compiled.LogEntry, wireValues []fr.Element, wir
 	for j := 0; j < len(entry.ToResolve); j++ {
 		wireID := entry.ToResolve[j]
 		if !wireInstantiated[wireID] {
-			panic("wire values was not instantiated")
+			toResolve = append(toResolve, "???")
+		} else {
+			toResolve = append(toResolve, wireValues[wireID].String())
 		}
-		toResolve = append(toResolve, wireValues[wireID].String())
 	}
 	return fmt.Sprintf(entry.Format, toResolve...)
 }
```
